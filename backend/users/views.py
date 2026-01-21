from django.contrib.auth import get_user_model, authenticate, login, logout
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, permissions, generics
from rest_framework.authtoken.models import Token
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

import random
import string
from .sms_service import SmsService
from .serializers import UserSerializer, CreditTransactionSerializer
from .models import CreditTransaction

User = get_user_model()

class CaptchaRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        new_key = CaptchaStore.generate_key()
        image_url = captcha_image_url(new_key)
        # Build absolute URI so that decoupled frontend can load the image
        full_url = request.build_absolute_uri(image_url)
        return Response({
            "key": new_key,
            "image_url": full_url
        })

class SendSMSView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        scene = request.data.get('scene', 'login')
        captcha_key = request.data.get('captcha_key')
        captcha_value = request.data.get('captcha_value')

        if not phone:
            return Response({"error": "ERROR_PHONE_REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify Captcha
        if not captcha_key or not captcha_value:
            return Response({"error": "ERROR_CAPTCHA_REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            captcha = CaptchaStore.objects.get(hashkey=captcha_key)
            if captcha.response.lower() != captcha_value.lower():
                return Response({"error": "ERROR_INVALID_CAPTCHA"}, status=status.HTTP_400_BAD_REQUEST)
            captcha.delete() # Consume captcha
        except CaptchaStore.DoesNotExist:
            return Response({"error": "ERROR_CAPTCHA_EXPIRED"}, status=status.HTTP_400_BAD_REQUEST)

        # Basic business logic: check user existence
        user_exists = User.objects.filter(phone_number=phone).exists()
        if scene == "register":
            if user_exists:
                return Response({"error": "ERROR_PHONE_ALREADY_REGISTERED"}, status=status.HTTP_400_BAD_REQUEST)
        elif scene in ["login", "reset_pwd"]:
            if not user_exists:
                return Response({"error": "ERROR_PHONE_NOT_REGISTERED"}, status=status.HTTP_404_NOT_FOUND)

        result = SmsService.send_code(phone, scene)
        if not result:
            return Response({"error": "ERROR_SMS_SERVICE_UNAVAILABLE"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        res_code = result.get('Code')
        if not res_code:
            res_code = result.get('code') # Try lowercase
        
        res_msg = result.get('Message', result.get('message', 'Unknown error'))

        if res_code == "OK":
            return Response({"message": "OK"})
        
        # User friendly error messages
        error_map = {
            "biz.FREQUENCY": "ERROR_SMS_TOO_FREQUENT",
            "isv.MOBILE_NUMBER_ILLEGAL": "ERROR_INVALID_PHONE_FORMAT",
            "isv.BUSINESS_LIMIT_CONTROL": "ERROR_SMS_LIMIT_EXCEEDED",
            "isv.AMOUNT_NOT_ENOUGH": "ERROR_SMS_QUOTA_EXHAUSTED",
        }
        user_error = error_map.get(res_code, f"{res_code}: {res_msg}")
        return Response({"error": user_error}, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        phone = request.data.get('phone')
        sms_code = request.data.get('sms_code')
        invite_code = request.data.get('invite_code')

        if not username or not password or not phone or not sms_code:
            return Response({"error": "ERROR_FIELDS_REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "ERROR_USERNAME_TAKEN"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(phone_number=phone).exists():
            return Response({"error": "ERROR_PHONE_BOUND"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify SMS Code
        verify_result = SmsService.verify_code(phone, sms_code)
        if not verify_result:
            return Response({"error": "ERROR_SMS_SERVICE_UNAVAILABLE"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        res_code = verify_result.get('Code')
        if res_code != "OK":
            error_map = {
                "isv.VERIFY_CODE_INVALID": "ERROR_INVALID_SMS_CODE",
                "isv.VERIFY_CODE_EXPIRED": "ERROR_SMS_CODE_EXPIRED",
            }
            return Response({"error": error_map.get(res_code, f"Verification failed: {res_code}")}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            invited_by = None
            if invite_code:
                invited_by = User.objects.filter(invitation_code=invite_code).exclude(phone_number=phone).first()
                # Note: We now always record the inviter, even if the limit is reached.
                # Validity is checked via user.is_invite_effective() later.

            user = User.objects.create_user(
                username=username, 
                password=password, 
                phone_number=phone,
                invited_by=invited_by
            )
            
            # Initial credits transaction
            initial_credits = 60
            CreditTransaction.objects.create(
                user=user,
                amount=initial_credits,
                balance_after=initial_credits,
                description="Welcome Bonus"
            )

            # Bonus for inviter
            # Only grant bonus if the invitation is effective (first 3 of the month)
            if invited_by and user.is_invite_effective():
                bonus = 60
                from django.db.models import F
                # Update inviter's credits atomically
                User.objects.filter(id=invited_by.id).update(credits=F('credits') + bonus)
                # Refresh object to get the updated credits for CreditTransaction log
                invited_by.refresh_from_db()
                
                CreditTransaction.objects.create(
                    user=invited_by,
                    amount=bonus,
                    balance_after=invited_by.credits,
                    description=f"Referral Bonus (Invited {username})"
                )
        
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user).data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        login_type = request.data.get('login_type', 'password') # 'password' or 'sms'
        
        if login_type == 'password':
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(username=username, password=password)
        else:
            phone = request.data.get('phone')
            sms_code = request.data.get('sms_code')
            if not phone or not sms_code:
                return Response({"error": "ERROR_PHONE_SMS_REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify SMS Code
            verify_result = SmsService.verify_code(phone, sms_code)
            if not verify_result:
                return Response({"error": "ERROR_SMS_SERVICE_UNAVAILABLE"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            res_code = verify_result.get('Code')
            if res_code != "OK":
                error_map = {
                    "isv.VERIFY_CODE_INVALID": "ERROR_INVALID_SMS_CODE",
                    "isv.VERIFY_CODE_EXPIRED": "ERROR_SMS_CODE_EXPIRED",
                }
                return Response({"error": error_map.get(res_code, f"Verification failed: {res_code}")}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.filter(phone_number=phone).first()
            if not user:
                return Response({"error": "ERROR_USER_NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)

        if user:
            # Refresh token on every login to reset the 48h timer
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            return Response({
                "user": UserSerializer(user).data,
                "token": token.key
            })
        return Response({"error": "ERROR_INVALID_CREDENTIALS"}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        sms_code = request.data.get('sms_code')
        new_password = request.data.get('new_password')

        if not phone or not sms_code or not new_password:
            return Response({"error": "ERROR_FIELDS_REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify SMS Code
        verify_result = SmsService.verify_code(phone, sms_code)
        if not verify_result:
            return Response({"error": "ERROR_SMS_SERVICE_UNAVAILABLE"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        res_code = verify_result.get('Code')
        if res_code != "OK":
            error_map = {
                "isv.VERIFY_CODE_INVALID": "ERROR_INVALID_SMS_CODE",
                "isv.VERIFY_CODE_EXPIRED": "ERROR_SMS_CODE_EXPIRED",
            }
            return Response({"error": error_map.get(res_code, f"Verification failed: {res_code}")}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone_number=phone).first()
        if not user:
            return Response({"error": "ERROR_USER_NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successfully"})

class ChangePhoneView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        new_phone = request.data.get('new_phone')
        sms_code = request.data.get('sms_code')
        scene = request.data.get('scene', 'bind_new') # 'bind_new' or 'modify_phone'

        if not new_phone or not sms_code:
            return Response({"error": "ERROR_PHONE_SMS_REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone_number=new_phone).exclude(id=request.user.id).exists():
            return Response({"error": "ERROR_PHONE_BOUND"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify SMS Code
        verify_result = SmsService.verify_code(new_phone, sms_code)
        if not verify_result:
            return Response({"error": "ERROR_SMS_SERVICE_UNAVAILABLE"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        res_code = verify_result.get('Code')
        if res_code != "OK":
            error_map = {
                "isv.VERIFY_CODE_INVALID": "ERROR_INVALID_SMS_CODE",
                "isv.VERIFY_CODE_EXPIRED": "ERROR_SMS_CODE_EXPIRED",
            }
            return Response({"error": error_map.get(res_code, f"Verification failed: {res_code}")}, status=status.HTTP_400_BAD_REQUEST)

        request.user.phone_number = new_phone
        request.user.save()
        return Response({"message": "Phone number updated successfully"})

class ChangeUsernameView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        new_username = request.data.get('username')
        if not new_username:
            return Response({"error": "ERROR_FIELDS_REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
            return Response({"error": "ERROR_USERNAME_TAKEN"}, status=status.HTTP_400_BAD_REQUEST)
            
        request.user.username = new_username
        request.user.save()
        return Response({"message": "Username updated successfully", "username": new_username})

class VerifyPasswordSmsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sms_code = request.data.get('sms_code')
        if not sms_code:
            return Response({"error": "ERROR_SMS_CODE_REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)

        phone = request.user.phone_number
        if not phone:
            return Response({"error": "ERROR_BIND_PHONE_FIRST"}, status=status.HTTP_400_BAD_REQUEST)

        verify_result = SmsService.verify_code(phone, sms_code)
        if not verify_result:
            return Response({"error": "ERROR_SMS_SERVICE_UNAVAILABLE"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        res_code = verify_result.get('Code')
        if res_code == "OK":
            # Set verification timestamp in user model (valid for 10 minutes)
            request.user.password_verified_at = timezone.now()
            request.user.save()
            return Response({"message": "OK"})
        
        error_map = {
            "isv.VERIFY_CODE_INVALID": "ERROR_INVALID_SMS_CODE",
            "isv.VERIFY_CODE_EXPIRED": "ERROR_SMS_CODE_EXPIRED",
        }
        return Response({"error": error_map.get(res_code, f"Verification failed: {res_code}")}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({"error": "ERROR_FIELDS_REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Check if SMS was verified in the last 10 minutes (stored in User model)
        verify_time = request.user.password_verified_at
        if not verify_time:
            return Response({"error": "ERROR_SMS_VERIFICATION_REQUIRED"}, status=status.HTTP_403_FORBIDDEN)
        
        if timezone.now() - verify_time > timedelta(minutes=10):
            request.user.password_verified_at = None
            request.user.save()
            return Response({"error": "ERROR_VERIFICATION_EXPIRED"}, status=status.HTTP_403_FORBIDDEN)

        # 2. Verify Old Password
        user = request.user
        if not user.check_password(old_password):
            return Response({"error": "ERROR_INCORRECT_PASSWORD"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Save New Password
        user.set_password(new_password)
        # Clear verification session
        user.password_verified_at = None
        user.save()
        
        # Update session to prevent logout
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        return Response({"message": "Password changed successfully"})

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Delete the token to log out
            request.user.auth_token.delete()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except (AttributeError, Token.DoesNotExist):
            return Response({"error": "ERROR_INVALID_TOKEN"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CreditHistoryView(generics.ListAPIView):
    serializer_class = CreditTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = CreditTransaction.objects.filter(user=self.request.user)
        
        # Filtering by days
        days = self.request.query_params.get('days')
        if days:
            try:
                days = int(days)
                start_date = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(timestamp__gte=start_date)
            except ValueError:
                pass
                
        return queryset.order_by('-timestamp')
