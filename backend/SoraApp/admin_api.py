from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAdminUser
from users.authentication import ExpiringTokenAuthentication
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from users.models import User, CreditTransaction, FAQ
from users.serializers import FAQSerializer
from videos.models import VideoTask
from .models import DailyStats, UserVisitLog, SystemSetting, ApiRequestLog
from django.db import models

from django.db.models import Sum, F
from datetime import timedelta
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

# Pagination Class
class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_dashboard_stats(request):
    """
    Returns statistics for the admin dashboard.
    """
    try:
        today = timezone.now().date()
        
        # KPI Cards
        total_users = User.objects.count()
        
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Real-time stats from primary tables
        from videos.models import VideoTask, PromptTask
        
        today_api_calls = 0 # Deprecated or needs real-time aggregation from logs if critical
        today_video_gen = VideoTask.objects.filter(created_at__gte=today_start).count()
        today_prompt_gen = PromptTask.objects.filter(created_at__gte=today_start).count()
        today_visits = UserVisitLog.objects.filter(timestamp__gte=today_start).count()
            
        # Totals
        total_api_calls = 0 # Deprecated
        total_video_gen = VideoTask.objects.count()
        total_prompt_gen = PromptTask.objects.count()
        total_visits = UserVisitLog.objects.count()

        # Detailed Video Stats by model and status
        from django.db.models import Count
        video_tasks_agg = VideoTask.objects.values('model', 'status').annotate(count=Count('id'))
        
        # Structure: { 'sora': {'SUCCESS': 0, 'FAILED': 0, 'TOTAL': 0}, 'sora2-pro': ... }
        video_detail_stats = {
            'sora': {'SUCCESS': 0, 'FAILED': 0, 'TOTAL': 0},
            'sora2-pro': {'SUCCESS': 0, 'FAILED': 0, 'TOTAL': 0}
        }
        
        for item in video_tasks_agg:
            m = item['model']
            s = item['status']
            c = item['count']
            
            # Map 'sora2' to 'sora' bucket for display compatibility
            target_key = m
            if m == 'sora2':
                target_key = 'sora'
            
            if target_key in video_detail_stats:
                if s in ['SUCCESS', 'FAILED']:
                    video_detail_stats[target_key][s] += c
                video_detail_stats[target_key]['TOTAL'] += c
        
        # Chart Data
        range_type = request.query_params.get('range', '30d')
        
        dates = []
        series_data = {
            'video': [],
            'prompt': [],
            'visits': []
        }
        
        if range_type == 'today':
            # Hourly Stats for Today
            from django.db.models.functions import TruncHour
            from django.db.models import Count
            # from .models import ApiRequestLog, UserVisitLog # MOVED TO TOP LEVEL
            
            # Initialize 24 hours
            hours_map = {i: {'video': 0, 'prompt': 0, 'visits': 0} for i in range(24)}
            
            # API Logs (Video & Prompt)
            api_logs = ApiRequestLog.objects.filter(timestamp__date=today).annotate(hour=TruncHour('timestamp')).values('hour', 'type').annotate(count=Count('id'))
            for log in api_logs:
                h = log['hour'].hour
                t = log['type']
                if t in ['video', 'prompt']:
                    hours_map[h][t] += log['count']
                    
            # Visit Logs
            visit_logs = UserVisitLog.objects.filter(timestamp__date=today).annotate(hour=TruncHour('timestamp')).values('hour').annotate(count=Count('id'))
            for log in visit_logs:
                h = log['hour'].hour
                hours_map[h]['visits'] += log['count']
                
            dates = [f"{i:02d}:00" for i in range(24)]
            for i in range(24):
                series_data['video'].append(hours_map[i]['video'])
                series_data['prompt'].append(hours_map[i]['prompt'])
                series_data['visits'].append(hours_map[i]['visits'])
                
        else:
            # Daily Stats (Last 30 Days)
            end_date = today
            start_date = end_date - timedelta(days=29)
            
            stats_qs = DailyStats.objects.filter(date__range=[start_date, end_date]).order_by('date')
            
            stats_dict = {
                s.date: {
                    'video': s.video_gen_count, 
                    'prompt': s.prompt_gen_count,
                    'visits': s.visit_count
                } 
                for s in stats_qs
            }
            
            current_date = start_date
            while current_date <= end_date:
                dates.append(current_date.strftime('%Y-%m-%d'))
                day_data = stats_dict.get(current_date, {'video': 0, 'prompt': 0, 'visits': 0})
                series_data['video'].append(day_data['video'])
                series_data['prompt'].append(day_data['prompt'])
                series_data['visits'].append(day_data['visits'])
                current_date += timedelta(days=1)
            
        return Response({
            'kpi': {
                'total_users': total_users,
                'today_visits': today_visits,
                'total_visits': total_visits,
                'today_video': today_video_gen,
                'total_video': total_video_gen,
                'today_prompt': today_prompt_gen,
                'total_prompt': total_prompt_gen,
                'video_detail': video_detail_stats
            },
            'chart_data': {
                'dates': dates,
                'series': [
                    {'name': 'Video Gen', 'data': series_data['video']},
                    {'name': 'Prompt Gen', 'data': series_data['prompt']},
                    {'name': 'Site Visits', 'data': series_data['visits']}
                ]
            }
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_user_list(request):
    """
    Returns a paginated list of users.
    """
    # Sorting
    sort_by = request.query_params.get('sort', '-date_joined')
    if sort_by == 'credits_desc':
        users = User.objects.all().order_by('-credits')
    elif sort_by == 'credits_asc':
         users = User.objects.all().order_by('credits')
    else:
        users = User.objects.all().order_by('-date_joined')
    
    # Search
    search_query = request.query_params.get('search', '')
    if search_query:
        users = users.filter(username__icontains=search_query) | \
                users.filter(email__icontains=search_query) | \
                users.filter(phone_number__icontains=search_query)

    paginator = UserPagination()
    result_page = paginator.paginate_queryset(users, request)
    
    data = []
    for user in result_page:
        data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
            'credits': user.credits,
            'date_joined': user.date_joined,
            'is_active': user.is_active,
            'is_active': user.is_active,
            'invitation_code': user.invitation_code,
            'invited_by': user.invited_by.username if user.invited_by else None,
            'is_effective': user.is_invite_effective() if user.invited_by else None
        })
        
    return paginator.get_paginated_response(data)

@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_user_update_credits(request, user_id):
    """
    Updates credits for a specific user.
    """
    user = get_object_or_404(User, pk=user_id)
    amount = request.data.get('amount')
    description = request.data.get('description', 'Admin adjustment')
    
    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid amount'}, status=400)
        
    user.credits += amount
    user.save()
    
    CreditTransaction.objects.create(
        user=user,
        amount=amount,
        balance_after=user.credits,
        description=description
    )

    # Check for conditional referral bonus (Same logic as add_credits command)
    print(f"DEBUG_ADMIN_CREDIT: amount={amount}, user={user.username}, invited_by={user.invited_by}, effective={user.is_invite_effective() if user.invited_by else 'N/A'}")
    if amount >= 399 and user.invited_by and user.is_invite_effective():
        inviter = user.invited_by
        bonus_amount = 99
        bonus_desc = f"Referral Top-up Bonus (Invitee {user.username} ID:{user.id} > 399)"

        # Check if this specific bonus has already been given
        already_rewarded = CreditTransaction.objects.filter(
            user=inviter,
            description=bonus_desc
        ).exists()

        if not already_rewarded:
            inviter.credits += bonus_amount
            inviter.save()
            
            CreditTransaction.objects.create(
                user=inviter,
                amount=bonus_amount,
                balance_after=inviter.credits,
                description=bonus_desc
            )
    
    return Response({
        'message': 'Credits updated successfully',
        'current_credits': user.credits
    })

@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_user_details(request, user_id):
    """
    Returns detailed stats for a user (credits, api usage).
    """
    user = get_object_or_404(User, pk=user_id)
    
    # Credit History
    credit_txs = CreditTransaction.objects.filter(user=user).order_by('-timestamp')
    credit_history = []
    for tx in credit_txs:
        credit_history.append({
            'id': tx.id,
            'amount': tx.amount,
            'balance_after': tx.balance_after,
            'description': tx.description,
            'timestamp': tx.timestamp
        })
        
    # API Usage History (last 30 days)
    today = timezone.now().date()
    end_date = today
    start_date = end_date - timedelta(days=29)
    
    from .models import UserApiUsage, UserVisitLog
    api_usage_qs = UserApiUsage.objects.filter(user=user, date__range=[start_date, end_date]).order_by('date')
    
    usage_dict = {s.date: {'video': s.video_gen, 'prompt': s.prompt_gen} for s in api_usage_qs}
    
    dates = []
    counts_video = []
    counts_prompt = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        day_data = usage_dict.get(current_date, {'video': 0, 'prompt': 0})
        counts_video.append(day_data['video'])
        counts_prompt.append(day_data['prompt'])
        current_date += timedelta(days=1)

    # Recent Visits
    visit_days = request.query_params.get('visit_days', '1') # Default 1 day (24h)
    
    visit_qs = UserVisitLog.objects.filter(user=user).order_by('-timestamp')
    
    if visit_days != 'all':
        try:
            days = int(visit_days)
            start_time = timezone.now() - timedelta(days=days)
            visit_qs = visit_qs.filter(timestamp__gte=start_time)
        except (ValueError, TypeError):
            # Fallback to 1 day if invalid
            start_time = timezone.now() - timedelta(days=1)
            visit_qs = visit_qs.filter(timestamp__gte=start_time)
            
    # Limit to 500 if 'all' or filtered, to prevent massive payloads
    # If users want full history, we should probably add pagination to this sub-table in the future.
    visits = visit_qs[:500] 
    
    visit_history = [{'timestamp': v.timestamp, 'ip': v.ip_address, 'path': v.path} for v in visits]
    
    # Visit Count (Total)
    total_visits = UserVisitLog.objects.filter(user=user).count()

    # Video Generation History (Last 20)
    video_tasks = VideoTask.objects.filter(user=user).order_by('-created_at')[:20]
    video_history = []
    for task in video_tasks:
        video_history.append({
            'id': task.id,
            'prompt': task.prompt,
            'model': task.model,
            'status': task.status,
            'created_at': task.created_at,
            'result_file': task.result_file.url if task.result_file else None,
            'error_message': task.failure_reason
        })

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'credits': user.credits,
            'date_joined': user.date_joined,
            'total_visits': total_visits
        },
        'credit_history': credit_history,
        'visit_history': visit_history,
        'video_history': video_history,
        'api_usage_chart': {
            'dates': dates,
            'series': [
                 {'name': 'Video Gen', 'data': counts_video},
                 {'name': 'Prompt Gen', 'data': counts_prompt}
            ]
        }
    })

@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAuthenticated])
def log_visit(request):
    """
    Explicitly log a visit from the frontend router.
    """
    path = request.data.get('path', '')
    ip = request.META.get('REMOTE_ADDR')
    
    # Create log
    UserVisitLog.objects.create(
        user=request.user,
        ip_address=ip,
        path=path
    )
    
    # Increment stats
    today = timezone.now().date()
    DailyStats.objects.get_or_create(date=today)
    DailyStats.objects.filter(date=today).update(visit_count=F('visit_count') + 1)
    
    return Response({'status': 'ok'})

@api_view(['DELETE'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_user_delete(request, user_id):
    """
    Delete a user.
    """
    user = get_object_or_404(User, pk=user_id)
    if user.is_superuser:
         return Response({'error': 'Cannot delete superuser'}, status=403)
         
    user.delete()
    return Response({'message': 'User deleted successfully'})

@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_user_change_password(request, user_id):
    """
    Change user password.
    """
    user = get_object_or_404(User, pk=user_id)
    new_password = request.data.get('password')
    
    if not new_password or len(new_password) < 6:
        return Response({'error': 'Password must be at least 6 characters'}, status=400)
        
    user.set_password(new_password)
    user.save()
    
    # Invalidate all existing tokens to force logout
    deleted_count, _ = Token.objects.filter(user=user).delete()
    print(f"DEBUG: Deleted {deleted_count} tokens for user {user.username}")
    
    
    return Response({'message': 'Password changed successfully'})

@api_view(['GET', 'POST'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_announcements(request):
    """
    GET: List all announcements.
    POST: Create a new announcement.
    """
    from users.models import Announcement
    
    if request.method == 'GET':
        anns = Announcement.objects.all().order_by('-created_at')
        data = [{
            'id': a.id, 
            'title': a.title, 
            'content': a.content, 
            'is_active': a.is_active,
            'created_at': a.created_at
        } for a in anns]
        return Response(data)
    
    elif request.method == 'POST':
        title = request.data.get('title')
        content = request.data.get('content')
        if not title or not content:
            return Response({'error': 'Title and content required'}, status=400)
            
        Announcement.objects.create(title=title, content=content)
        return Response({'message': 'Announcement created'})

@api_view(['DELETE', 'PATCH'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_announcement_detail(request, pk):
    """
    DELETE: Delete announcement.
    PATCH: Update status/content.
    """
    from users.models import Announcement
    ann = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'DELETE':
        ann.delete()
        return Response({'message': 'Deleted'})
        
    elif request.method == 'PATCH':
        if 'is_active' in request.data:
            ann.is_active = request.data['is_active']
        if 'title' in request.data:
            ann.title = request.data['title']
        if 'content' in request.data:
            ann.content = request.data['content']
        ann.save()
        return Response({'message': 'Updated'})

@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_logs_list(request):
    """
    Returns paginated global logs (Video & Prompt history).
    """
    from videos.models import VideoTask, PromptTask
    from django.db.models import Value, CharField, F
    
    # Filter by username if provided
    username = request.query_params.get('username')
    
    # 1. Fetch VideoTasks
    v_tasks = VideoTask.objects.all().select_related('user')
    if username:
        v_tasks = v_tasks.filter(user__username__icontains=username)
    
    v_list = []
    for t in v_tasks:
        # User requested: for video, show generation_time if available
        gen_time_str = "-"
        if t.generation_time:
            gen_time_str = f"{t.generation_time:.1f}s"
            
        v_list.append({
            'id': t.id,
            'user': t.user.username if t.user else "Unknown",
            'type': 'VIDEO',
            'prompt': t.prompt or "",
            'model': t.model or "sora",
            'status': t.status,
            'created_at': t.created_at,
            'duration': f"{t.duration or 0}s",
            'generation_time': gen_time_str
        })

    # 2. Fetch PromptTasks
    p_tasks = PromptTask.objects.all().select_related('user')
    if username:
        p_tasks = p_tasks.filter(user__username__icontains=username)
        
    p_list = []
    for t in p_tasks:
        p_list.append({
            'id': t.id,
            'user': t.user.username if t.user else "Unknown",
            'type': 'PROMPT',
            'prompt': t.raw_prompt or "",
            'model': t.model or "sora",
            'status': t.status,
            'created_at': t.created_at,
            'duration': "-", # Prompt tasks don't have video duration
            'generation_time': "-" # Prompt tasks don't have generation time recorded in the same way
        })

    # 3. Combine and sort by created_at descending
    all_logs = sorted(v_list + p_list, key=lambda x: x['created_at'], reverse=True)

    try:
        from django.core.paginator import Paginator
        page_num = request.query_params.get('page', 1)
        limit = 20
        paginator = Paginator(all_logs, limit)
        page_obj = paginator.get_page(page_num)
        
        return Response({
            'count': paginator.count,
            'next': page_obj.has_next() if page_obj.has_next() else None,
            'previous': page_obj.has_previous() if page_obj.has_previous() else None,
            'results': list(page_obj) # page_obj is already a list of dicts
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_create_user(request):
    """
    Create a user directly (bypass SMS verification).
    """
    username = request.data.get('username')
    password = request.data.get('password')
    credits = request.data.get('credits', 60)
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)
        
    if User.objects.filter(username=username).exists():
         return Response({'error': 'Username taken'}, status=400)
         
    user = User.objects.create_user(username=username, password=password)
    user.credits = int(credits)
    user.save()
    
    # Log transaction
    CreditTransaction.objects.create(
        user=user,
        amount=user.credits,
        balance_after=user.credits,
        description="Initial Admin Creation"
    )
    
    return Response({'message': 'User created', 'id': user.id})

@api_view(['GET', 'POST'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_faqs(request):
    """
    GET: List all FAQs.
    POST: Create a new FAQ.
    """
    if request.method == 'GET':
        faqs = FAQ.objects.all()
        serializer = FAQSerializer(faqs, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = FAQSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PATCH', 'DELETE'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_faq_detail(request, pk):
    """
    GET: Get detail.
    PATCH: Update FAQ.
    DELETE: Delete FAQ.
    """
    faq = get_object_or_404(FAQ, pk=pk)
    
    if request.method == 'GET':
        serializer = FAQSerializer(faq)
        return Response(serializer.data)
        
    elif request.method == 'PATCH':
        serializer = FAQSerializer(faq, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
        
    elif request.method == 'DELETE':
        faq.delete()
        return Response(status=204)


@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_get_sora_provider(request):
    """获取当前的 sora2 provider"""
    provider = SystemSetting.get_setting("SORA_PROVIDER", "marketai")
    return Response({'provider': provider})

@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAdminUser])
def admin_update_sora_provider(request):
    """更新 sora2 provider"""
    provider = request.data.get('provider')
    if provider not in ['marketai', 'grsai']:
        return Response({'error': 'Invalid provider'}, status=400)
    
    setting, created = SystemSetting.objects.get_or_create(key="SORA_PROVIDER")
    setting.value = provider
    setting.description = "Sora2 API Provider (marketai or grsai)"
    setting.save()
    
    return Response({'message': 'Provider updated successfully', 'provider': provider})
