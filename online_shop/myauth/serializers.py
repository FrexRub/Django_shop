import re
import logging

from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Profile

log = logging.getLogger(__name__)

# PATTERN_PASSWORD = (
#     r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
# )
PATTERN_PASSWORD = r'^(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[0-9])(?=.*?[!"#\$%&\(\)\*\+,-\.\/:;<=>\?@[\]\^_`\{\|}~])[a-zA-Z0-9!\$%&\(\)\*\+,-\.\/:;<=>\?@[\]\^_`\{\|}~]{8,}$'
PATTERN_PHONE = r"^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$"


class ResultSerializer(serializers.Serializer):
    message = serializers.CharField()


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField()


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        log.info("Начало валидации пароля")

        if re.search(PATTERN_PASSWORD, value):
            log.info("Пароль соответствует политике безопасности")
            return value
        else:
            log.info("Пароль не соответствует политике безопасности")
            raise serializers.ValidationError("Invalid password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user)

        return user


class ProfileSerializerGet(serializers.Serializer):
    fullName = serializers.CharField(allow_blank=True, max_length=150, style={'input_type': 'fullName'})
    email = serializers.CharField(allow_blank=True, style={'input_type': 'email'})
    phone = serializers.CharField(allow_blank=True, style={'input_type': 'phone'})
    avatar = serializers.DictField(child=serializers.CharField(allow_blank=True))


class ProfileSerializerPost(serializers.Serializer):
    fullName = serializers.CharField(allow_blank=True, max_length=150)
    email = serializers.CharField(allow_blank=True)
    phone = serializers.CharField(allow_blank=True)

    def validate_phone(self, value):
        log.info("Начало валидации телефона")

        if re.search(PATTERN_PHONE, value):
            log.info("Телефон указан верно")
            return value
        else:
            log.info("Телефон указан неверно")
            raise serializers.ValidationError("Invalid phone")


class UserAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar"]

    def save(self, *args, **kwargs):
        if self.instance.avatar:
            self.instance.avatar.delete()
        return super().save(*args, **kwargs)


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(allow_blank=True)

    def validate_password(self, value):
        log.info("Начало валидации пароля")

        if re.search(PATTERN_PASSWORD, value):
            log.info("Пароль соответствует политике безопасности")
            return value
        else:
            log.info("Пароль не соответствует политике безопасности")
            raise serializers.ValidationError("Invalid password")
