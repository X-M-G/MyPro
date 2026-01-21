from django.urls import path
from . import views
from . import admin_api
from . import user_api

urlpatterns = [
    # Dashboard HTML View (optional, if we keep simpleui access)
    path('', views.admin_dashboard_view, name='admin_dashboard'),
    
    # New Admin JSON APIs
    path('dashboard/stats/', admin_api.admin_dashboard_stats, name='admin_dashboard_stats'),
    path('users/', admin_api.admin_user_list, name='admin_user_list'),
    
    # Specific paths MUST be before generic <int:user_id> if using re_path, but for path it's fine. 
    # However, to be absolutely safe and clean:
    path('users/<int:user_id>/credits/', admin_api.admin_user_update_credits, name='admin_user_update_credits'),
    path('users/<int:user_id>/delete/', admin_api.admin_user_delete, name='admin_user_delete'),
    path('users/<int:user_id>/password/', admin_api.admin_user_change_password, name='admin_user_change_password'),
    path('users/<int:user_id>/', admin_api.admin_user_details, name='admin_user_details'),
    
    path('log-visit/', admin_api.log_visit, name='log_visit'),

    # Announcements
    path('announcements/', admin_api.admin_announcements, name='admin_announcements'),
    path('announcements/<int:pk>/', admin_api.admin_announcement_detail, name='admin_announcement_detail'),

    # Global Logs
    path('logs/', admin_api.admin_logs_list, name='admin_logs_list'),
    
    # Create User
    path('users/create/', admin_api.admin_create_user, name='admin_create_user'),

    # FAQs
    path('faqs/', admin_api.admin_faqs, name='admin_faqs'),
    path('faqs/<int:pk>/', admin_api.admin_faq_detail, name='admin_faq_detail'),

    # System Settings
    path('settings/sora-provider/', admin_api.admin_get_sora_provider, name='admin_get_sora_provider'),
    path('settings/sora-provider/update/', admin_api.admin_update_sora_provider, name='admin_update_sora_provider'),

    # User facing
    path('user/announcements/', user_api.list_announcements, name='user_announcements'),
    path('user/announcements/unread/', user_api.get_unread_announcements, name='user_unread_announcements'),
    path('user/announcements/acknowledge/', user_api.acknowledge_announcement, name='user_acknowledge_announcement'),
    path('user/faqs/', user_api.list_faqs, name='user_faqs'),
]


