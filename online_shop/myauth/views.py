import logging
import json

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer


log = logging.getLogger(__name__)


class UserRegistrationView(APIView):
    def post(self, request):
        # POST data в формате QueryDict, все данны передаются в качестве ключа словаря
        data_req = json.loads(list(request.POST.dict().items())[0][0])

        log.info("Запрос на регистрацию пользователя %s", data_req.get("username"))
        print("data_req", data_req)
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


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
