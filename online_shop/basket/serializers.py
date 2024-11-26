import logging

import locale

from rest_framework import serializers
from django.db.models import Avg, Count, Value, FloatField
from django.db.models.functions import Coalesce
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from shopapp.models import (
    Product,
    Category,
)

from shopapp.serializers import (
    ProductImageSerializer,
    SpecificationSerializer,
    ReviewSerializer,
)

log = logging.getLogger(__name__)

# для отображения названий месяцев на русском
locale.setlocale(
    category=locale.LC_ALL,
    locale="Russian",
)


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

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_rating(self, obj):
        return Product.objects.filter(pk=obj.pk).aggregate(
            rating=Coalesce(Avg("reviews__rate", output_field=FloatField()), Value(0.0))
        )["rating"]

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
