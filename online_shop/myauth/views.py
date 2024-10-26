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


# @extend_schema_view(
#     create=extend_schema(
#         summary="Авторизация пользователя",
#         request=UserLoginSerializer,
#         responses={
#             status.HTTP_200_OK: ResultSerializer,
#             status.HTTP_400_BAD_REQUEST: ResultSerializer,
#             status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
#                 response=None,
#                 description="Что-то пошло не так",
#             ),
#         },
#     ),
# )
class UserLoginView(APIView):
    @extend_schema(
        tags=["auth"], request=UserLoginSerializer, responses=ResultSerializer
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
        tags=["auth"], request=UserRegistrationSerializer, responses=ResultSerializer
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

    @extend_schema(tags=["auth"], request=None, responses=ResultSerializer)
    def post(self, request):
        log.info("Выход пользователя %s из системы", self.request.user.username)
        logout(request)
        return Response({"message": "Logout Successful"}, status=status.HTTP_200_OK)


@extend_schema(tags=["profile"])
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user: User = self.request.user
        profile: Profile = get_profile_user(user)
        log.info("Изменение данных профиля пользователя %s", self.request.user)
        print(self.request.user, "->", request.data)
        serializer = ProfileSerializerPost(data=request.data)
        if serializer.is_valid():
            # Запись данных в модель пользователя
            user.first_name = request.data.get("fullName")

            if (
                    User.objects.filter(email=request.data.get("email"))
                            .exclude(first_name=user.first_name)
                            .exists()
            ):
                return Response(
                    {"err": "Email in use"}, status=status.HTTP_400_BAD_REQUEST
                )

            user.email = request.data.get("email")
            user.save()

            # Запись данных в модель профиля пользователя
            if (
                    Profile.objects.filter(phone_number=request.data.get("phone"))
                            .exclude(user=user)
                            .exists()
            ):
                return Response(
                    {"err": "Phone in use"}, status=status.HTTP_400_BAD_REQUEST
                )
            profile.phone_number = request.data.get("phone")
            profile.save()
            log.info("Изменение данных профиля пользователя внесены")
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            log.error("Данные некорректны %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            log.info("Успешная валидация данных пользователя %s", serializer.data)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        log.error("Данные в форме регистрации некорректны %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["profile"])
class UserAvatarUpload(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        profile = get_profile_user(self.request.user)
        serializer = UserAvatarSerializer(data=request.data, instance=profile)
        if serializer.is_valid():
            serializer.save()
            # return redirect(request.META["HTTP_REFERER"])
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["profile"])
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

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
