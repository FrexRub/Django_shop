"""
URL configuration for online_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from myauth.views import (
    ProfileView,
    UserRegistrationView,
    LogoutAPIView,
    UserLoginView,
)


router = DefaultRouter()
# router.register("profile", ProfileView)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("frontend.urls")),
    path("api/sign-up/", UserRegistrationView.as_view(), name="sign_up"),
    path("api/sign-out/", LogoutAPIView.as_view(), name="logout"),
    path("api/sign-in/", UserLoginView.as_view(), name="sign_in"),
    path("api/profile/", ProfileView.as_view(), name="profile"),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
