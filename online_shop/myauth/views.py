import logging
import json
from dataclasses import asdict

import django.http
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    ProfileSerializer,
    UserAvatarSerializer,
)
from .models import Profile
from services.schemas import ProfileSchema

log = logging.getLogger(__name__)


def get_profile_user(user: User) -> Profile:
    """
    Поиск профиля пользователя
    :param user: User
        объект конкретного пользователя
    :return: Profile
        профиль пользователя
    """
    profile: Profile = Profile.objects.select_related("user").filter(user=user).first()
    return profile


class UserLoginView(APIView):
    def post(self, request):
        # POST data в формате QueryDict, все данные передаются в качестве ключа словаря
        data_log = json.loads(list(request.POST.dict().items())[0][0])
        username = data_log.get("username")
        log.info("Запрос на аутентификацию пользователя %s", username)

        # Проверка правильности введенных данных
        serializer = UserLoginSerializer(
            data={
                "username": username,
                "password": data_log.get("password"),
            }
        )
        if serializer.is_valid():
            # Проверка наличия пользователя в БД
            try:
                user: User = User.objects.get(username=username)
            except User.DoesNotExist:
                log.error("Пользователь %s не найден", username)
                raise exceptions.AuthenticationFailed("No such user")

            # Проверка введенного пароля
            if user.check_password(data_log.get("password")):
                login(request=self.request, user=user)
                log.info("Пользователь %s авторизовался", username)
            else:
                log.info("Неверный пароль", username)
                return Response(
                    {"message": "Invalid password"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return Response(
                {"message": "User login successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            log.error("Данные в форме аутентификации некорректны %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(APIView):
    def post(self, request):
        # POST data в формате QueryDict, все данные передаются в качестве ключа словаря
        data_req = json.loads(list(request.POST.dict().items())[0][0])

        log.info("Запрос на регистрацию пользователя %s", data_req.get("username"))

        if User.objects.filter(username=data_req.get("username")).exists():
            return Response(
                {"message": "Username is already in use"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UserRegistrationSerializer(
            data={
                "username": data_req.get("username"),
                "password": data_req.get("password"),
            }
        )
        if serializer.is_valid():
            serializer.save()
            log.info("Пользователь %s зарегистрирован", data_req.get("username"))
            user = authenticate(
                self.request,
                username=data_req.get("username"),
                password=data_req.get("password"),
            )
            log.debug("Login new user as %s", data_req.get("username"))
            login(request=self.request, user=user)

            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            log.error("Данные в форме регистрации некорректны %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    next_page = reverse_lazy("home")

    def post(self, request):
        # Directly logs out the user who made the request and deletes their session.
        logout(request)
        # Return success response
        return Response({"detail": "Logout Successful"}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile: Profile = (
            Profile.objects.select_related("user")
            .filter(user=self.request.user)
            .first()
        )
        log.info("Загрузка профиля пользователя %s", self.request.user)
        res_profile = ProfileSchema(
            fullName=profile.user.first_name,
            email=profile.user.email,
            phone=profile.phone_number,
            avatar={
                "src": "".join(["/media/", str(profile.avatar)]),
                "alt": profile.slug,
            },
        )

        serializer = ProfileSerializer(data=asdict(res_profile))
        if serializer.is_valid():
            log.info("Успешная валидация данных пользователя %s", serializer.data)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        log.error("Данные в форме регистрации некорректны %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAvatarUpload(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        profile = get_profile_user(self.request.user)
        serializer = UserAvatarSerializer(data=request.data, instance=profile)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            # return redirect(request.META["HTTP_REFERER"])
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    def post(self, request, format=None):
        profile = get_profile_user(self.request.user)
