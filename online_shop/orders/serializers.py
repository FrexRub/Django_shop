import locale

from rest_framework import serializers
from django.db.models import Avg, Count, Value, FloatField
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from orders.models import Order, OrderInfoBasket
from shopapp.serializers import ProductImageSerializer
from shopapp.models import (
    Product,
    Category,
)


class ProductOrderSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    # вывод только id из связанной модели Category
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="id"
    )
    # расчет количества отзывов о продукте
    reviews = serializers.SerializerMethodField()
    # создание дополнительного поля с расчетным средним значением
    rating = serializers.SerializerMethodField()
    # создание поля со значением количества товара в корзине
    count = serializers.SerializerMethodField()
    # создание поля со значением цены товара в корзине
    price = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.INT)
    def get_count(self, obj):
        order_info = OrderInfoBasket.objects.get(
            order=self.context["order"], product=obj
        )
        return order_info.count_in_order

    @extend_schema_field(OpenApiTypes.DECIMAL)
    def get_price(self, obj):
        order_info = OrderInfoBasket.objects.get(
            order=self.context["order"], product=obj
        )
        return order_info.price_in_order

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_rating(self, obj):
        return Product.objects.filter(pk=obj.pk).aggregate(
            rating=Coalesce(Avg("reviews__rate", output_field=FloatField()), Value(0.0))
        )["rating"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_reviews(self, obj):
        return Product.objects.filter(pk=obj.pk).aggregate(
            reviews=Count("reviews__id")
        )["reviews"]

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


class OrderSerializer(serializers.ModelSerializer):
    products = ProductOrderSerializer(source="basket", many=True, read_only=True)
    createdAt = serializers.DateTimeField(source="created_at")
    fullName = serializers.CharField(source="user.first_name")
    email = serializers.CharField(source="user.email")
    phone = serializers.CharField(source="user.profile.phone_number")
    deliveryType = serializers.CharField(source="delivery_type")
    paymentType = serializers.CharField(source="payment_type")
    totalCost = serializers.CharField(source="total_cost")

    class Meta:
        model = Order
        fields = (
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        )
