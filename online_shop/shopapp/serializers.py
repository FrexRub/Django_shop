import logging

from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    Product,
    ProductImage,
    Tag,
    Review,
    Category,
    Specification,
)

log = logging.getLogger(__name__)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ["name"]


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = (
            "name",
            "value",
        )


# class UserNameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ("first_name",)
#         # fields = ("first_name", "email", )


class ReviewSerializer(serializers.ModelSerializer):
    # вывод имени из связанной модели User
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field="first_name"
    )
    # вывод email из связанной модели User
    # email = serializers.SlugRelatedField(
    #     queryset=User.objects.all(), slug_field="email"
    # )
    # ToDo email

    class Meta:
        model = Review
        fields = (
            "author",
            # "email",
            "text",
            "rate",
            "date",
        )


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = (
            "src",
            "alt",
        )


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = SpecificationSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    # вывод списка только значений из пары ключ: значение
    tags = serializers.StringRelatedField(many=True)
    # ToDo rating
    # вывод id из связанной модели Category
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="id"
    )

    class Meta:
        model = Product
        depth = 1
        fields = (
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "fullDescription",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "specifications",
        )
