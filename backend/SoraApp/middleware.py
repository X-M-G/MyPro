from .models import DailyStats, UserApiUsage, UserVisitLog, ApiRequestLog
from django.utils import timezone
from django.db.models import F
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser

class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Helper to get user via Token if not already authenticated (e.g. by SessionMiddleware)
        user = request.user
        if not user.is_authenticated and 'HTTP_AUTHORIZATION' in request.META:
            auth_header = request.META['HTTP_AUTHORIZATION']
            if auth_header.startswith('Token '):
                key = auth_header.split(' ')[1]
                try:
                    token = Token.objects.get(key=key)
                    user = token.user
                except Token.DoesNotExist:
                    pass

        # 1. Track Website Visits (via auth/me check on app load)
        if user.is_authenticated and request.path == '/api/auth/me/':
            try:
                today = timezone.now().date()
                DailyStats.objects.get_or_create(date=today)
                
                # Check if this user visited today
                has_visited_today = UserVisitLog.objects.filter(
                    user=user, 
                    timestamp__date=today
                ).exists()
                
                # Log detailed visit
                # Attempt to get the referer (frontend path)
                referer = request.META.get('HTTP_REFERER', '')
                
                UserVisitLog.objects.create(
                    user=user,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    path=referer
                )
                
                # Only increment unique daily visit count if first time
                # Or count every session as a visit? Requirement says "record visit time, total count"
                # Let's count total hits to /me as "visits" for now, or maybe session based.
                # Simplest interpretation: Just increment specific counter for analytics
                DailyStats.objects.filter(date=today).update(visit_count=F('visit_count') + 1)
                
            except Exception as e:
                print(f"Error logging visit: {e}")

        # 2. Track API Usage
        if request.path.startswith('/api/'):
            try:
                today = timezone.now().date()
                DailyStats.objects.get_or_create(date=today)
                DailyStats.objects.filter(date=today).update(api_call_count=F('api_call_count') + 1)
                
                api_type = None
                if '/videos/generate/' in request.path:
                    api_type = 'video'
                    DailyStats.objects.filter(date=today).update(video_gen_count=F('video_gen_count') + 1)
                elif '/videos/prompt/generate/' in request.path:
                    api_type = 'prompt'
                    DailyStats.objects.filter(date=today).update(prompt_gen_count=F('prompt_gen_count') + 1)
                
                # Log detailed API request for hourly stats
                if api_type:
                     from .models import ApiRequestLog
                     ApiRequestLog.objects.create(
                         user=user if user.is_authenticated else None,
                         endpoint=request.path,
                         method=request.method,
                         type=api_type
                     )

                # Log per-user usage
                if user.is_authenticated:
                    UserApiUsage.objects.get_or_create(user=user, date=today)
                    updates = {'count': F('count') + 1}
                    if api_type == 'video':
                        updates['video_gen'] = F('video_gen') + 1
                    elif api_type == 'prompt':
                        updates['prompt_gen'] = F('prompt_gen') + 1
                        
                    UserApiUsage.objects.filter(user=user, date=today).update(**updates)
                    
            except Exception as e:
                # Silently fail to avoid blocking the request
                print(f"Error logging request: {e}")
                
        response = self.get_response(request)
        return response
