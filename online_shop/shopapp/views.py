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
from myauth.models import Profile

from .serializers import (
    TagSerializer,
    ProductSerializer,
    ProductShortSerializer,
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


class GetUserForReviewApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Для заполнения данных пользователя в форме отзыва (изменения в исходный код фронтенда)
        :param request:
            параметры запроса
        :return:
        """
        user: User = request.user
        email: str = user.email
        author: str = user.first_name if user.first_name else user.username
        return Response(
            {
                "author": author,
                "email": email,
            },
            status=status.HTTP_200_OK,
        )


class ProductReviewApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        author = request.data.get("author")
        email = request.data.get("email")
        text = request.data.get("text")
        rate = request.data.get("rate")

        user: User = self.request.user
        product: Product = get_object_or_404(Product, pk=pk)
        print("author", author)
        print("email", email)
        print("text", text)
        print("rate", rate)

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
        # ToDo pagination and Filter
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
        serializer = ProductShortSerializer(products, many=True)
        data = {
            "items": serializer.data,
            "currentPage": 5,
            "lastPage": 10,
        }

        return Response(
            data,
            status=status.HTTP_200_OK,
        )
