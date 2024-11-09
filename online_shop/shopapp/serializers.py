import logging

import locale

from rest_framework import serializers
from django.db.models import Avg, Count
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

# для отображения названий месяцев на русском
locale.setlocale(
    category=locale.LC_ALL,
    locale="Russian",
)


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


class ReviewDBSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("text", "rate")


class ReviewSerializer(serializers.ModelSerializer):
    # вывод имени из связанной модели User
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field="first_name"
    )
    # создание дополнительного поля email с данными из модели User
    email = serializers.SerializerMethodField()
    date = serializers.DateTimeField(format="%d/%b/%Y %H:%M")

    def get_email(self, obj):
        user: User = User.objects.first()
        return user.email

    class Meta:
        model = Review
        fields = (
            "author",
            "email",
            "text",
            "rate",
            "date",
        )


class ProductImageSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    def get_src(self, obj):
        return "".join(["/media/", str(obj.src)])

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
    # вывод только id из связанной модели Category
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="id"
    )
    # создание дополнительного поля с расчетным средним значением
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return Product.objects.aggregate(rating=Avg("reviews__rate"))["rating"]

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
            "rating",
        )


class ProductShortSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    # вывод только id из связанной модели Category
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="id"
    )
    # расчет количества отзывов о продукте
    reviews = serializers.SerializerMethodField()
    # создание дополнительного поля с расчетным средним значением
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return Product.objects.aggregate(rating=Avg("reviews__rate"))["rating"]

    def get_reviews(self, obj):
        return Product.objects.aggregate(reviews=Count("reviews__id"))["reviews"]

    class Meta:
        model = Product
        # для вывода данных из связанных таблиц, а не только перечень id
        depth = 1
        fields = (
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        )
