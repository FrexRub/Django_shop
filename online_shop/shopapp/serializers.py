import logging

from rest_framework import serializers

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


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        exclude = (
            "slug",
            "tags",
        )
