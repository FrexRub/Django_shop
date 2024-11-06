import logging
import json
from dataclasses import asdict

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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
    ProductShortSerializer,
    CatalodSerializer,
)

from services.schemas import CategoriesSchema

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


class ProductReviewApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        author = request.data.get("author")
        email = request.data.get("author")
        text = request.data.get("author")
        rate = request.data.get("author")

        user: User = self.request.user
        product: Product = get_object_or_404(ProductReviewApiView, pk=pk)

        # ToDo serilazed


class CategoriesApiView(APIView):
    def get(self, request):
        log.info("Загрузка категорий товара")
        data_сategories = []
        сategories = Category.objects.all()
        for сategory in сategories:
            data_сategory = CategoriesSchema(
                id=сategory.id,
                title=сategory.title,
                image={
                    "src": "".join(["/media/", str(сategory.image)]),
                    "alt": сategory.slug,
                },
            )
            res_сategory = asdict(data_сategory)
            res_сategory["subcategories"] = list()
            res_сategory["subcategories"].append(asdict(data_сategory))
            data_сategories.append(res_сategory)

        # serializer = ProfileSerializerGet(data=asdict(res_profile))

        return Response(
            data_сategories,
            status=status.HTTP_200_OK,
        )


class CatalogApiView(APIView):
    def get(self, request):
        filter = request.GET.get("filter")
        currentPage = request.GET.get("currentPage")
        category = request.GET.get("category")
        sort = request.GET.get("sort")
        sortType = request.GET.get("sortType")
        tags = request.GET.get("tags")
        limit = request.GET.get("limit")

        print("filter", filter)
        print("currentPage", currentPage)
        print("category", category)
        print("sort", sort)
        print("sortType", sortType)
        print("tags", tags)
        print("limit", limit)

        products = Product.objects.all()
        serializer = CatalodSerializer(products)
        print(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
