import logging
import json

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import (
    Product,
    ProductImage,
    Tag,
    Review,
    Category,
    Specification,
)

from .serializers import (
    TagSerializer,
    ProductSerializer,
)

log = logging.getLogger(__name__)


class TagApiView(APIView):
    def get(self, request):
        tag_id = request.data.get("category")
        log.info("Запрос тега продукта по его номеру %s", tag_id)
        if tag_id is None:
            log.info("Не указан номер в запросе тега продукта")
            return Response(
                {"massage": "Не указан номер в запросе тега продукта"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tag: Tag = get_object_or_404(Tag, pk=tag_id)
        serializer = TagSerializer(tag)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ProductApiView(APIView):
    def get(self, request, pk: int):
        product: Product = (
            Product.objects.filter(pk=pk)
            .annotate(rating=Avg("reviews__rate"))
            .select_related("category")
            .prefetch_related(
                "tags", "images", "specifications", "reviews", "reviews__author"
            )
            .first()
        )

        if product is None:
            return Response(
                {"massage": "Product not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ProductSerializer(product)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
