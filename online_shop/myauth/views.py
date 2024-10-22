import logging
import json

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer

log = logging.getLogger(__name__)


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


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        log.info("Logout user %s", self.request.user)
        context = super().get_context_data(**kwargs)
        return context


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
