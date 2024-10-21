import logging

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer

from .models import Profile

log = logging.getLogger(__name__)

class UserRegistrationView(APIView):
    def post(self, request):
        log.info("Запрос на регистрацию пользователя %s", request.data)
        name = request.data.get("name")
        # if name.find(" ") > 0:
        #     first_name, last_name = tuple(name.split())
        # else:
        #     first_name, last_name = (name, "")
        first_name, last_name = ("SS", "FF")
        password = request.data.get("password")
        print(name, first_name, last_name, password)
        # serializer = UserRegistrationSerializer(data=request.data)
        serializer = UserRegistrationSerializer(data={
            "username": request.data.get("username"),
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
        })
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            log.error("Данные в форме некорректны")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
