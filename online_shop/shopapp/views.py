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
from rest_framework.pagination import PageNumberPagination

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
    ReviewDBSerializer,
)

from services.schemas import CategoriesSchema

log = logging.getLogger(__name__)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class TagApiView(APIView):
    def get(self, request):
        category_id = request.GET.get("category")
        log.info("Запрос тегов категории товаров по её номеру %s", category_id)
        if category_id is None:
            log.info("В запросе не указан номер категории товаров")
            return Response(
                {"massage": "В запросе не указан номер категории товаров"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tags: Tag = Tag.objects.filter(category__id=category_id)
        log.info(
            "Список тегов для категории товаров с номером %s подготовлен", category_id
        )
        serializer = TagSerializer(tags, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ProductApiView(APIView):
    def get(self, request, pk: int):
        log.info("Запрос информации по продукту с id %s", pk)
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
            log.info("Продукт с id %s не найден", pk)
            return Response(
                {"massage": "Product not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ProductSerializer(product)
        log.info("Запрос информации по продукту с id %s успешно выполнен", pk)
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
        log.info(
            "Заполнение контактной информации в форме отзыва о товаре пользователя %s",
            request.user.username,
        )
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
        log.info("Создание отзыва о товаре пользователя %s", request.user.username)

        user: User = self.request.user
        product: Product = get_object_or_404(Product, pk=pk)

        # Данные передаются в сериализатор как request.data
        # text = request.data.get("text")
        # rate = request.data.get("rate")
        serializer = ReviewDBSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(author=user, product=product)
            log.info("Отзыв пользователя %s о товаре создан", request.user.username)

            return Response(
                {"message": "The review has been created"},
                status=status.HTTP_201_CREATED,
            )
        else:
            log.error("Данные в форме отзыва некорректны", serializer.errors)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

        # ToDo Filter
        filter = request.GET.get("filter")
        sort = request.GET.get("sort")
        sortType = request.GET.get("sortType")
        tags = request.GET.get("tags")

        category_id = int(request.GET.get("category"))
        currentPage = int(request.GET.get("currentPage"))
        limit = int(request.GET.get("limit"))

        print("filter", filter)
        print("currentPage", currentPage)
        print("category", category_id)
        print("sort", sort)
        print("sortType", sortType)
        print("tags", tags)
        print("limit", limit)

        category: Category = get_object_or_404(Category, pk=category_id)

        queryset: Product = (
            Product.objects.filter(category=category)
            .select_related("category")
            .prefetch_related(
                "tags", "images", "specifications", "reviews", "reviews__author"
            )[:limit]
        )

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)

        serializer = ProductShortSerializer(result_page, many=True)
        data = {
            "items": serializer.data,
            # "currentPage": paginator.page.number,
            "currentPage": currentPage,
            "lastPage": paginator.page.paginator.count,
        }

        return Response(
            data,
            status=status.HTTP_200_OK,
        )
