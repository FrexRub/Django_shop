import logging
import locale
from datetime import datetime
from zoneinfo import ZoneInfo

from django.conf import settings
from rest_framework import serializers
from django.db.models import Avg, Count, Value, FloatField
from django.db.models.functions import Coalesce
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from shopapp.models import (
    Product,
    Category,
    Sales,
)

from shopapp.serializers import (
    ProductImageSerializer,
    SpecificationSerializer,
    ReviewSerializer,
)

from .cart import Cart

log = logging.getLogger(__name__)

# для отображения названий месяцев на русском
locale.setlocale(
    category=locale.LC_ALL,
    locale="Russian",
)


class BasketDataSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    count = serializers.IntegerField()


class BasketSerializer(serializers.ModelSerializer):
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

    # создание поля со значением количества товара в корзине
    count = serializers.SerializerMethodField()

    # создание поля цены товара с учетом скидки
    price = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_rating(self, obj):
        return Product.objects.filter(pk=obj.pk).aggregate(
            rating=Coalesce(Avg("reviews__rate", output_field=FloatField()), Value(0.0))
        )["rating"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_count(self, obj):
        cart = Cart(self.context["request"])
        prod = cart.get(obj.pk)
        return prod["quantity"]

    @extend_schema_field(OpenApiTypes.DECIMAL)
    def get_price(self, obj):
        date_now = datetime.now(tz=ZoneInfo(settings.TIME_ZONE))
        product_discount = Sales.objects.filter(product__id=obj.pk).first()

        if product_discount and (
            product_discount.dateFrom <= date_now <= product_discount.dateTo
        ):
            log.info(
                "У товара с id%s цена со скидкой %s"
                % (obj.pk, product_discount.salePrice)
            )
            return product_discount.salePrice
        else:
            return obj.price

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
