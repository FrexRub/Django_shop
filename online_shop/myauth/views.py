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
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    ProfileSerializerGet,
    ProfileSerializerPost,
    UserAvatarSerializer,
    PasswordSerializer,
    ResultSerializer,
)
from .models import Profile
from online_shop import settings
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
    @extend_schema(
        tags=["auth"],
        summary="Вход пользователя в личный кабинет",
        request=UserLoginSerializer,
        responses={
            status.HTTP_200_OK: ResultSerializer,
            status.HTTP_400_BAD_REQUEST: ResultSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            )
        },
        examples=[
            OpenApiExample(
                "Login example",
                description="Пример заполнения полей для логирования",
                value={
                    "username": "User1",
                    "password": "qwertY&01",
                },
                status_codes=[str(status.HTTP_200_OK)]
            )
        ],
    )
    def post(self, request):
        if request.data.get("username"):
            username = request.data.get("username")
            password = request.data.get("password")
        else:
            # POST data в формате QueryDict, все данные передаются в качестве ключа словаря
            data_log = json.loads(list(request.POST.dict().items())[0][0])
            username = data_log.get("username")
            password = data_log.get("password")

        log.info("Запрос на аутентификацию пользователя %s", username)
        log.info("DEBUG %s", settings.DEBUG)

        # Проверка правильности введенных данных
        serializer = UserLoginSerializer(
            data={
                "username": username,
                "password": password,
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
            if user.check_password(password):
                login(request=self.request, user=user)
                log.info("Пользователь %s авторизовался", username)
            else:
                log.info("Неверный пароль пользователя %s", username)
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
    @extend_schema(
        tags=["auth"],
        summary="Регистрация пользователя на сайте",
        request=UserRegistrationSerializer,
        responses={
            status.HTTP_201_CREATED: ResultSerializer,
            status.HTTP_400_BAD_REQUEST: ResultSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            )
        },
        examples=[
            OpenApiExample(
                "Registration example",
                description="Пример заполнения полей для регистрации",
                value={
                    "username": "User1",
                    "password": "qwertY&01",
                },
                status_codes=[str(status.HTTP_201_CREATED)]
            )
        ],
    )
    def post(self, request):
        if request.data.get("username"):
            username = request.data.get("username")
            password = request.data.get("password")
        else:
            # POST data в формате QueryDict, все данные передаются в качестве ключа словаря
            data_req = json.loads(list(request.POST.dict().items())[0][0])
            username = data_req.get("username")
            password = data_req.get("password")

        log.info("Запрос на регистрацию пользователя %s", username)

        if User.objects.filter(username=username).exists():
            return Response(
                {"message": "Username is already in use"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UserRegistrationSerializer(
            data={
                "username": username,
                "password": password,
            }
        )
        if serializer.is_valid():
            serializer.save()
            log.info("Пользователь %s зарегистрирован", username)
            user = authenticate(
                self.request,
                username=username,
                password=password,
            )
            log.info("Логирование нового пользователя как %s", username)
            login(request=self.request, user=user)

            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            log.error("Данные в форме регистрации некорректны %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    next_page = reverse_lazy("home")

    @extend_schema(
        tags=["auth"],
        summary="Выход пользователя из личного кабинета",
        request=None,
        responses={
            status.HTTP_200_OK: ResultSerializer,
            status.HTTP_400_BAD_REQUEST: ResultSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            )
        },
        examples=[
            OpenApiExample(
                "Registration example",
                description="Пример заполнения полей для регистрации",
                value={
                    "username": "User1",
                    "password": "qwertY&01",
                },
                status_codes=[str(status.HTTP_201_CREATED)]
            )
        ],
    )
    def post(self, request):
        log.info("Выход пользователя %s из системы", self.request.user.username)
        logout(request)
        return Response({"message": "Logout Successful"}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["profile"],
        summary="Редактирование профиля пользователя",
        request=ProfileSerializerPost,
        responses={
            status.HTTP_200_OK: ResultSerializer,
            status.HTTP_400_BAD_REQUEST: ResultSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            )
        },
        examples=[
            OpenApiExample(
                "Profile edit example",
                description="Пример заполнения полей для редактирования профиля",
                value={
                    "fullName": "Алексей Иванов",
                    "phone": "+79151232358",
                    "email": "alex@shop.com",
                },
                status_codes=[str(status.HTTP_200_OK)]
            )
        ],
    )
    def post(self, request, format=None):
        user: User = self.request.user
        profile: Profile = get_profile_user(user)
        log.info("Изменение данных профиля пользователя %s", self.request.user)
        serializer = ProfileSerializerPost(data=request.data)
        if serializer.is_valid():
            # Запись данных в модель пользователя
            user.first_name = request.data.get("fullName")

            if (
                    User.objects.filter(email=request.data.get("email"))
                            .exclude(username=user.username)
                            .exists()
            ):
                log.info("Пользователь с данным email уже зарегистрирован")
                return Response(
                    {"message": "Email in use"}, status=status.HTTP_400_BAD_REQUEST
                )

            user.email = request.data.get("email")

            # Запись данных в модель профиля пользователя
            if (
                    Profile.objects.select_related("user")
                            .filter(phone_number=request.data.get("phone"))
                            .exclude(user__username=user.username)
                            .exists()
            ):
                log.info("Пользователь с данным телефонов уже зарегистрирован")
                return Response(
                    {"message": "Phone in use"}, status=status.HTTP_400_BAD_REQUEST
                )
            profile.phone_number = request.data.get("phone")
            profile.save()
            user.save()
            log.info("Изменение данных профиля пользователя внесены")
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            log.error("Данные некорректны %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["profile"],
        summary="Загрузка профиля пользователя",
        request=None,
        responses={
            status.HTTP_200_OK: ProfileSerializerGet,
            status.HTTP_400_BAD_REQUEST: ResultSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            )
        },
        examples=[
            OpenApiExample(
                "Profile example",
                description="Пример профиля",
                value={
                    "fullName": "Annoying Orange",
                    "email": "no-reply@mail.ru",
                    "phone": "88002000600",
                    "avatar": {
                        "src": "/3.png",
                        "alt": "Image alt string"
                    }
                },
                status_codes=[str(status.HTTP_200_OK)]
            )
        ],
    )
    def get(self, request):
        profile: Profile = get_profile_user(self.request.user)

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

        serializer = ProfileSerializerGet(data=asdict(res_profile))
        if serializer.is_valid():
            log.info("Успешная валидация данных пользователя %s", self.request.user)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        log.error("Данные в форме регистрации некорректны %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAvatarUpload(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["profile"],
        summary="Изменение профиля аватара",
        request=None,
        responses={
            status.HTTP_200_OK: None,
            status.HTTP_400_BAD_REQUEST: ResultSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            )
        },
    )
    def post(self, request, format=None):
        profile = get_profile_user(self.request.user)
        serializer = UserAvatarSerializer(data=request.data, instance=profile)
        if serializer.is_valid():
            serializer.save()
            # return redirect(request.META["HTTP_REFERER"])
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["profile"],
        summary="Изменение пароля пользователя",
        request=PasswordSerializer,
        responses={
            status.HTTP_200_OK: ResultSerializer,
            status.HTTP_400_BAD_REQUEST: ResultSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            )
        },
        examples=[
            OpenApiExample(
                "Password edit example",
                description="Пример изменения пароля",
                value={
                    "passwordCurrent": "old password",
                    "password": "new password",
                    "passwordReply": "reply new password",
                },
                status_codes=[str(status.HTTP_200_OK)]
            )
        ],
    )
    def post(self, request, format=None):
        user: User = self.request.user
        log.info("Изменения текущего пароля пользователя %s", user.username)

        if user.check_password(request.data.get("passwordCurrent")):
            log.info("Текущий пароль пользователя %s указан верно", user.username)
        else:
            log.info("Неверный пароль пользователя %s", user.username)
            return Response(
                {"message": "Invalid password"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.data.get("password") != request.data.get("passwordReply"):
            log.info("Пароли не совпадают %s", user.username)
            return Response(
                {"message": "Passwords don't match"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PasswordSerializer(data={"password": request.data.get("password")})
        if serializer.is_valid():
            user.set_password(request.data.get("password"))
            user.save()
            log.info("Успешная смена пароля пользователя %s", user.username)
            return Response(
                {"message": "ok"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
