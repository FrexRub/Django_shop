import logging

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)

from basket.cart import Cart
from shopapp.views import Product
from basket.serializers import BasketSerializer, BasketDataSerializer

log = logging.getLogger(__name__)


class BasketApiView(APIView):
    @extend_schema(
        tags=["basket"],
        summary="Добавление товара в корзину",
        request=BasketDataSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=BasketSerializer(many=True),
                description="The review has been created",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=None,
                description="No Product matches the given query",
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            ),
        },
        examples=[
            OpenApiExample(
                "Example",
                description="Пример заполнения полей для добавления товара",
                value={
                    "id": 1,
                    "count": 2,
                },
                status_codes=[str(status.HTTP_201_CREATED)],
            )
        ],
    )
    def post(self, request):
        """
        Добавление товара в корзину
        :param request:
        :return:
        """
        id_product = int(request.data.get("id"))
        count_product = int(request.data.get("count"))

        cart = Cart(request)
        product: Product = get_object_or_404(Product, pk=id_product)

        if product.count == 0:
            log.info("Товар с id %s отсутствует на складе" % id_product)
            return Response(
                {"message": "The product is out of stock"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if product.count > count_product:
            product.count -= count_product
        else:
            count_product = product.count
            product.count = 0

        product.save()

        cart.add(product=product, quantity=count_product)
        log.info(
            "Добавление в корзину продукта с id %s в количестве %s"
            % (id_product, count_product)
        )

        list_id = cart.list_id_products()
        products = (
            Product.objects.filter(id__in=list_id)
            .select_related("category")
            .prefetch_related(
                "tags", "images", "specifications", "reviews", "reviews__author"
            )
            .order_by("id")
        )
        serializer = BasketSerializer(products, many=True, context={"request": request})

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["basket"],
        summary="Вывод содержания корзины",
        responses={
            status.HTTP_200_OK: BasketSerializer(many=True),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            ),
        },
    )
    def get(self, request):
        """
        Вывод содержания корзины
        :param request:
        :return:
        """
        cart = Cart(request)
        list_id = cart.list_id_products()
        products = (
            Product.objects.filter(id__in=list_id)
            .select_related("category")
            .prefetch_related(
                "tags", "images", "specifications", "reviews", "reviews__author"
            )
            .order_by("id")
        )
        serializer = BasketSerializer(products, many=True, context={"request": request})
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["basket"],
        summary="Удаление товара из корзины",
        request=BasketDataSerializer,
        responses={
            status.HTTP_200_OK: BasketSerializer(many=True),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=None,
                description="No Product matches the given query",
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            ),
        },
        examples=[
            OpenApiExample(
                "Example",
                description="Пример заполнения полей для удаления товара",
                value={
                    "id": 1,
                    "count": 2,
                },
                status_codes=[str(status.HTTP_200_OK)],
            )
        ],
    )
    def delete(self, request):
        """
        Удаление товара из корзины
        :param request:
        :return:
        """
        id_product = int(request.data.get("id"))
        count_product = int(request.data.get("count"))
        log.info(
            "Удаление из корзины продукта с id %s в количестве %s"
            % (id_product, count_product)
        )
        cart = Cart(request)
        cart.remove(id_product, count_product)

        product: Product = get_object_or_404(Product, pk=id_product)
        product.count += count_product
        product.save()
        log.info(
            "Возвращение на склад из корзины продукта с id %s в количестве %s"
            % (id_product, count_product)
        )

        list_id = cart.list_id_products()
        products = (
            Product.objects.filter(id__in=list_id)
            .select_related("category")
            .prefetch_related(
                "tags", "images", "specifications", "reviews", "reviews__author"
            )
            .order_by("id")
        )
        serializer = BasketSerializer(products, many=True, context={"request": request})
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
