import logging
from dataclasses import asdict

from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiExample,
)

from .models import (
    Product,
    Tag,
    Sales,
    Category,
)

from .serializers import (
    TagSerializer,
    ProductSerializer,
    ProductShortSerializer,
    ReviewDBSerializer,
    SalesSerializer,
)

from services.schemas import CategoriesSchema
from .utils import sorted_products

log = logging.getLogger(__name__)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class TagApiView(APIView):
    @extend_schema(
        tags=["tags"],
        summary="Вывод списка тегов по номеру категории товара",
        responses={
            status.HTTP_200_OK: TagSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=None,
                description="В запросе не указан номер категории товаров",
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            ),
        },
        parameters=[
            OpenApiParameter(
                name="category",
                location=OpenApiParameter.QUERY,
                description="номер категории товаров",
                required=False,
                type=int,
            ),
        ],
    )
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
    @extend_schema(
        tags=["product"],
        summary="Вывод информации по продукту с id",
        responses={
            status.HTTP_200_OK: ProductSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=None,
                description="Product not found",
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            ),
        },
    )
    def get(self, request, pk: int):
        log.info("Запрос информации по продукту с id %s", pk)
        product: Product = (
            Product.objects.filter(pk=pk)
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoriesApiView(APIView):
    def get(self, request):
        log.info("Загрузка категорий товара")
        # список всех каталогов товаров (категорий)
        all_сategories = []
        # выборка родительский каталогов
        сategories = Category.objects.filter(subcategories__isnull=True)
        for сategory in сategories:
            data_сategory = CategoriesSchema(
                id=сategory.id,
                title=сategory.title,
                image={
                    "src": "".join(["/media/", str(сategory.image)]),
                    "alt": сategory.slug,
                },
            )
            # Добавление подкаталогов товаров
            res_сategory = asdict(data_сategory)
            res_сategory["subcategories"] = list()

            subcategories = Category.objects.filter(subcategories=сategory)
            for subcategory in subcategories:
                data_сategory = CategoriesSchema(
                    id=subcategory.id,
                    title=subcategory.title,
                    image={
                        "src": "".join(["/media/", str(subcategory.image)]),
                        "alt": subcategory.slug,
                    },
                )
                res_сategory["subcategories"].append(asdict(data_сategory))

            all_сategories.append(res_сategory)

        return Response(
            all_сategories,
            status=status.HTTP_200_OK,
        )


class CatalogApiView(APIView):
    def get(self, request):
        current_page = int(request.GET.get("currentPage"))

        queryset = sorted_products(request)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)

        serializer = ProductShortSerializer(result_page, many=True)
        data = {
            "items": serializer.data,
            "currentPage": current_page,
            "lastPage": paginator.page.paginator.count,
        }

        return Response(
            data,
            status=status.HTTP_200_OK,
        )


class PopularListApiView(ListAPIView):
    # ToDo фильтрация по количеству покупок
    queryset = (
        Product.objects.all()
        .select_related("category")
        .prefetch_related(
            "tags", "images", "specifications", "reviews", "reviews__author"
        )
        .order_by("id")[:8]
    )
    serializer_class = ProductShortSerializer

    @method_decorator(cache_page(5 * 60 * 60, key_prefix="popular"))
    def get(self, *args, **kwargs):
        res = super().get(*args, **kwargs)
        res.data = res.data["results"]
        return res


class LimitListApiView(ListAPIView):
    queryset = (
        Product.objects.filter(count__range=(1, 10))
        .select_related("category")
        .prefetch_related(
            "tags", "images", "specifications", "reviews", "reviews__author"
        )
        .order_by("id")[:16]
    )
    serializer_class = ProductShortSerializer

    @method_decorator(cache_page(2 * 60 * 60, key_prefix="limited"))
    def get(self, *args, **kwargs):
        res = super().get(*args, **kwargs)
        res.data = res.data["results"]
        return res


class BannersListApiView(APIView):
    def get(self, request):
        cache_key = "catalog_banners"
        data_banners = cache.get(cache_key)

        if data_banners is None:
            log.info("Create banners list")

            category: Category = (
                Category.objects.values("pk").exclude(subcategories__isnull=True).all()
            )

            data_banners = list()
            list_pk_category = [i_category["pk"] for i_category in category]

            for id_category in list_pk_category:
                queryset = (
                    Product.objects.filter(category__pk=id_category)
                    .select_related("category")
                    .prefetch_related(
                        "tags", "images", "specifications", "reviews", "reviews__author"
                    )
                    .first()
                )

                if queryset:
                    log.info("Category %s add in banners list", id_category)
                    serializer = ProductShortSerializer(queryset)
                    data_banners.append(serializer.data)
                else:
                    log.info("Category %s not product for banners list", id_category)

            # сохранение данных кеша по ключу
            cache.set(cache_key, data_banners, 30 * 60 * 60)
            log.info("Записываем данные в кеш %s", cache_key)
        else:
            log.info("Получаем данные из кеша %s", cache_key)

        return Response(
            data_banners,
            status=status.HTTP_200_OK,
        )


class SalesListApiView(APIView):
    def get(self, request):
        current_page = int(request.GET.get("currentPage"))
        queryset = (
            Sales.objects.select_related("product")
            .prefetch_related("product__images")
            .all()
        )

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)

        serializer = SalesSerializer(result_page, many=True)

        data = {
            "items": serializer.data,
            "currentPage": current_page,
            "lastPage": paginator.page.paginator.count,
        }

        return Response(
            data,
            status=status.HTTP_200_OK,
        )
