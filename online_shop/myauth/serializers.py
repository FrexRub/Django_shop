import logging

from rest_framework import serializers
from django.contrib.auth.models import User


log = logging.getLogger(__name__)

class UserRegistrationSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    # def validate(self, attrs):
    #     if attrs["password"] != attrs["password2"]:
    #         raise serializers.ValidationError(
    #             {"password": "Password fields didn't match."}
    #         )
    #     return attrs

    def create(self, validated_data):
        log.info("Регистрация пользователя с ником %s", validated_data['username'])
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data["password"],
        )
        log.info("Пользователь %s создан", user)
        return user
