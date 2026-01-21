from django.urls import path
from .views import (
    LoginView, LogoutView, UserInfoView, CreditHistoryView, RegisterView,
    SendSMSView, CaptchaRefreshView, ResetPasswordView, ChangePhoneView,
    ChangePasswordView, VerifyPasswordSmsView, ChangeUsernameView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserInfoView.as_view(), name='user-info'),
    path('credits/history/', CreditHistoryView.as_view(), name='credit-history'),
    path('send-sms/', SendSMSView.as_view(), name='send-sms'),
    path('captcha-refresh/', CaptchaRefreshView.as_view(), name='captcha-refresh'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-phone/', ChangePhoneView.as_view(), name='change-phone'),
    path('change-username/', ChangeUsernameView.as_view(), name='change-username'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('verify-password-sms/', VerifyPasswordSmsView.as_view(), name='verify-password-sms'),
]
