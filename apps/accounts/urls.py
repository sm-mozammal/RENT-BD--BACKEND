from django.urls import path
from .views import (
    OTPRequestView,
    OTPVerifyView,
    UserProfileView,
    NIDVerifyView,
    RegisterView,
    PasswordLoginView,
    RoleSwitchView,
    ChangePasswordView,
    LogoutView,
)

urlpatterns = [
    path('otp/request/', OTPRequestView.as_view(), name='otp-request'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp-verify'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', PasswordLoginView.as_view(), name='password-login'),
    path('role/switch/', RoleSwitchView.as_view(), name='role-switch'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('nid-verify/', NIDVerifyView.as_view(), name='nid-verify'),
]
