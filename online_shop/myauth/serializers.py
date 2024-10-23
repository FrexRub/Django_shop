from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Profile


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField()


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user)

        return user


class ProfileSerializer(serializers.Serializer):
    fullName = serializers.CharField(allow_blank=True, max_length=150)
    email = serializers.CharField(allow_blank=True)
    phone = serializers.CharField(allow_blank=True)
    avatar = serializers.DictField(child=serializers.CharField(allow_blank=True))
