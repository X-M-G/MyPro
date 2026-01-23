from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import VideoTask
from .serializers import VideoTaskSerializer
from .services import SoraService
from users.models import CreditTransaction
from django.db import transaction


# views.py (或包含此代码的文件)
# views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from django.db import transaction
from .models import VideoTask
from .serializers import VideoTaskSerializer
from .services import SoraService
from users.models import CreditTransaction

# 【配置】建议放入 settings.py，这里为了方便直接写
MAX_USER_CONCURRENT_TASKS = 2  # 每个用户同时只能生成 1 个
MAX_SYSTEM_CONCURRENT_TASKS = 6 # 系统总共同时只能生成 5 个（根据你的4G内存设定）

class GenerateVideoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        prompt = request.data.get('prompt')
        ratio = request.data.get('ratio', '16:9')
        duration = request.data.get('duration', 15) # Default 15 as requested
        model = request.data.get('model', 'sora')
        ref_image = request.data.get('ref_image') 

        # Determine credit cost
        cost = 300 if model == 'sora2-pro' else 30
        
        if not prompt:
            return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

        # --- 【新增】并发控制逻辑开始 ---
        
        # 1. 检查该用户是否有正在进行的任务
        user_active_count = VideoTask.objects.filter(
            user=user, 
            status__in=['PENDING', 'PROCESSING']
        ).count()
        
        if user_active_count >= MAX_USER_CONCURRENT_TASKS:
            return Response(
                {"error": "You have another tasks in progress. Please wait for it to finish."}, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # 2. 检查系统总负载
        system_active_count = VideoTask.objects.filter(
            status__in=['PENDING', 'PROCESSING']
        ).count()
        
        if system_active_count >= MAX_SYSTEM_CONCURRENT_TASKS:
            return Response(
                {"error": "System is busy processing many videos. Please try again in a moment."}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
            
        # --- 【新增】并发控制逻辑结束 ---

        if user.credits < cost:
            return Response({"error": f"Insufficient credits. This model requires {cost} credits."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                user.credits -= cost
                user.save()

                CreditTransaction.objects.create(
                    user=user,
                    amount=-cost,
                    balance_after=user.credits,
                    description=f"Video generation cost ({model})"
                )

                task = VideoTask.objects.create(
                    user=user,
                    prompt=prompt,
                    ratio=ratio,
                    duration=duration,
                    model=model
                )

            SoraService.generate_video(task.id, prompt, ratio, duration, ref_image, model)

            return Response(
                VideoTaskSerializer(task, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





from .models import PromptTask, PromptHistory

class PromptGenerationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        raw_prompt = request.data.get('prompt')
        style = request.data.get('style', 'Cinematic')
        language = request.data.get('language', 'English')
        duration = request.data.get('duration', '15s')
        model = request.data.get('model', 'sora')

        if not raw_prompt:
            return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 检查积分
        from django.conf import settings
        cost = getattr(settings, 'PROMPT_GENERATION_COST', 20)
        
        # Check active task to prevent spam
        active_task = PromptTask.objects.filter(
            user=user, 
            status__in=['PENDING', 'PROCESSING']
        ).exclude(model='gpt-5.1-chat').first()
        
        if active_task:
            return Response({
                "message": "You have an active prompt generation task.",
                "task_id": active_task.id
            }, status=status.HTTP_200_OK)

        if user.credits < cost:
            return Response(
                {"error": f"Insufficient credits. You have {user.credits} credits, but need {cost} credits to generate a prompt."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                 user.credits -= cost
                 user.save()
                 
                 CreditTransaction.objects.create(
                    user=user,
                    amount=-cost,
                    balance_after=user.credits,
                    description=f"Prompt Optimization Task ({style}, {language})"
                 )
            
                 task = PromptTask.objects.create(
                     user=user,
                     raw_prompt=raw_prompt,
                     style=style,
                     language=language,
                     duration=duration,
                     model=model,
                     status='PENDING'
                 )

            # Start Async Task
            SoraService.start_prompt_generation_task(task.id)
            
            return Response({
                "task_id": task.id,
                "message": "Prompt generation started."
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from .serializers import PromptTaskSerializer, PromptHistorySerializer

class PromptTaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            task = PromptTask.objects.get(pk=pk, user=request.user)
            serializer = PromptTaskSerializer(task)
            return Response(serializer.data)
        except PromptTask.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


class ActivePromptTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Find latest pending or processing prompt task (not chat)
        task = PromptTask.objects.filter(
            user=request.user, 
            status__in=['PENDING', 'PROCESSING']
        ).exclude(model='gpt-5.1-chat').order_by('-created_at').first()
        
        if task:
            serializer = PromptTaskSerializer(task)
            return Response(serializer.data)
        return Response({"active": False})


class AIChatAssistantView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        prompt = request.data.get('prompt')

        if not prompt:
            return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 检查积分
        from django.conf import settings
        cost = getattr(settings, 'PROMPT_GENERATION_COST', 20)
        
        # Check active task to prevent spam
        active_task = PromptTask.objects.filter(
            user=user, 
            status__in=['PENDING', 'PROCESSING'],
            model='gpt-5.1-chat'
        ).first()
        
        if active_task:
            return Response({
                "message": "You have an active chat task.",
                "task_id": active_task.id
            }, status=status.HTTP_200_OK)

        if user.credits < cost:
            return Response(
                {"error": f"Insufficient credits. You have {user.credits} credits, but need {cost} credits for a chat."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                 user.credits -= cost
                 user.save()
                 
                 CreditTransaction.objects.create(
                    user=user,
                    amount=-cost,
                    balance_after=user.credits,
                    description=f"AI Chat Assistant Task"
                 )
            
                 task = PromptTask.objects.create(
                     user=user,
                     raw_prompt=prompt,
                     style='Chat',
                     language='N/A',
                     duration='N/A',
                     model='gpt-5.1-chat',
                     status='PENDING'
                 )

            # Start Async Task
            SoraService.start_chat_assistant_task(task.id)
            
            return Response({
                "task_id": task.id,
                "message": "Chat processing started."
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActiveChatTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Find latest pending or processing chat task
        task = PromptTask.objects.filter(
            user=request.user, 
            status__in=['PENDING', 'PROCESSING'],
            model='gpt-5.1-chat'
        ).order_by('-created_at').first()
        
        if task:
            serializer = PromptTaskSerializer(task)
            return Response(serializer.data)
        return Response({"active": False})


# 【新增】：获取历史记录的视图
class PromptHistoryListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 获取当前用户的所有历史记录，按时间倒序
        histories = PromptHistory.objects.filter(user=request.user)
        
        # 可选：分页
        page = request.query_params.get('page', 1)
        page_size = 10
        start = (int(page) - 1) * page_size
        end = start + page_size
        
        paginated_histories = histories[start:end]
        total_count = histories.count()
        
        serializer = PromptHistorySerializer(paginated_histories, many=True)
        
        return Response({
            "results": serializer.data,
            "count": total_count,
            "page": int(page),
            "page_size": page_size
        })


# 【新增】：删除单条历史记录
class PromptHistoryDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            history = PromptHistory.objects.get(pk=pk, user=request.user)
            history.delete()
            return Response({"message": "History deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except PromptHistory.DoesNotExist:
            return Response({"error": "History not found"}, status=status.HTTP_404_NOT_FOUND)

        
        

class PromptGenerationView2(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        raw_prompt = request.data.get('prompt')
        style = request.data.get('style', 'Cinematic')
        language = request.data.get('language', 'English')

        if not raw_prompt:
            return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 检查积分
        from django.conf import settings
        cost = getattr(settings, 'PROMPT_GENERATION_COST', 15)
        
        if user.credits < cost:
            print(f"Insufficient credits. You have {user.credits} credits, but need {cost} credits to generate a prompt.")
            return Response(
                {"error": f"Insufficient credits. You have {user.credits} credits, but need {cost} credits to generate a prompt."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            optimized_prompt = SoraService.generate_refined_prompt(
                request.user, raw_prompt, style, language
            )
            return Response({"prompt": optimized_prompt})
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class PromptGenerationView1(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        raw_prompt = request.data.get('prompt')
        style = request.data.get('style', 'Cinematic')
        language = request.data.get('language', 'English')

        if not raw_prompt:
            return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            optimized_prompt = SoraService.generate_refined_prompt(
                request.user, raw_prompt, style, language
            )
            return Response({"prompt": optimized_prompt})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VideoListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tasks = VideoTask.objects.filter(user=request.user).order_by('-created_at')
        # 【修改点】：传入 context
        serializer = VideoTaskSerializer(tasks, many=True, context={'request': request})
        return Response(serializer.data)


class VideoDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            task = VideoTask.objects.get(pk=pk, user=request.user)
            # 【修改点】：传入 context
            serializer = VideoTaskSerializer(task, context={'request': request})
            return Response(serializer.data)
        except VideoTask.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)


from django.http import FileResponse, Http404, HttpResponseForbidden
from rest_framework.views import APIView
from rest_framework import permissions  # 注意这里
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from .models import VideoTask
import os


class VideoStreamView(APIView):
    # 1. 关键修改：允许任何人访问这个接口，因为由于 <video> 标签的限制，请求没带 Auth Header
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        # 2. 获取 URL 中的 token 参数
        token = request.GET.get('token')

        if not token:
            return HttpResponseForbidden("Missing access token")

        signer = TimestampSigner()

        try:
            # 3. 验证签名
            # max_age=3600 表示链接在 1 小时内有效（防止链接泄露后永久有效）
            # unsign 会返回原始数据（即 pk），如果签名被篡改或过期则抛出异常
            original_pk = signer.unsign(token, max_age=3600)

            # 4. 确保 URL 里的 pk 和 签名解出来的 pk 一致 (双重保险)
            if str(original_pk) != str(pk):
                return HttpResponseForbidden("Invalid token")

        except SignatureExpired:
            return HttpResponseForbidden("Link expired")
        except BadSignature:
            return HttpResponseForbidden("Invalid signature")

        # 5. 签名验证通过，开始获取文件
        try:
            # 注意：这里我们不再需要 check request.user，因为签名本身就是一种授权
            # 只要你能生成这个签名，说明你之前通过了 VideoTaskSerializer 的权限检查
            task = VideoTask.objects.get(pk=pk)

            if not task.result_file:
                raise Http404("Video file not found")

            file_path = task.result_file.path

            if not os.path.exists(file_path):
                raise Http404("File missing on server")

            # 6. 返回视频流
            response = FileResponse(open(file_path, 'rb'), content_type='video/mp4')
            return response

        except VideoTask.DoesNotExist:
            raise Http404("Video not found")
