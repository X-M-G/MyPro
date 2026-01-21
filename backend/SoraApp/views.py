from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from users.models import User
from .models import DailyStats
from django.db.models import Sum
from datetime import timedelta

@staff_member_required
def admin_dashboard_view(request):
    today = timezone.now().date()
    
    # KPI Cards
    total_users = User.objects.count()
    
    try:
        today_stats = DailyStats.objects.get(date=today)
        today_api_calls = today_stats.api_call_count
    except DailyStats.DoesNotExist:
        today_api_calls = 0
        
    total_api_calls = DailyStats.objects.aggregate(total=Sum('api_call_count'))['total'] or 0
    
    # Chart Data (Last 30 days)
    end_date = today
    start_date = end_date - timedelta(days=29)
    
    stats_qs = DailyStats.objects.filter(date__range=[start_date, end_date]).order_by('date')
    
    # Prepare data for chart (ensure all days are present)
    dates = []
    counts = []
    
    stats_dict = {stats.date: stats.api_call_count for stats in stats_qs}
    
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        counts.append(stats_dict.get(current_date, 0))
        current_date += timedelta(days=1)
    
    context = {
        'total_users': total_users,
        'today_api_calls': today_api_calls,
        'total_api_calls': total_api_calls,
        'chart_dates': dates,
        'chart_counts': counts,
    }
    
    return render(request, 'admin_dashboard.html', context)
