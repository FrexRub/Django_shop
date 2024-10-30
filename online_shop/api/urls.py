from django.urls import path

from myauth.views import (
    ProfileView,
    UserRegistrationView,
    LogoutAPIView,
    UserLoginView,
    UserAvatarUpload,
    ChangePasswordView,
)

app_name = "api"

urlpatterns = [
    path("sign-up/", UserRegistrationView.as_view(), name="sign_up"),
    path("sign-out/", LogoutAPIView.as_view(), name="logout"),
    path("sign-in/", UserLoginView.as_view(), name="sign_in"),
    path("profile/password/", ChangePasswordView.as_view(), name="edit_password"),
    path("profile/avatar/", UserAvatarUpload.as_view(), name="avatar"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
