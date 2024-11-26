import logging

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .cart import Cart
from shopapp.views import Product
from .serializers import BasketSerializer

log = logging.getLogger(__name__)


class BasketApiView(APIView):
    # ToDo учет количества товара при добавлении в корзину и удалении
    def post(self, request):
        print("Добавление товара ", request.data)
        id_product = int(request.data.get("id"))
        count_product = int(request.data.get("count"))
        log.info(
            "Добавление в корзину продукта с id %s в количестве %s"
            % (id_product, count_product)
        )
        cart = Cart(request)
        product: Product = get_object_or_404(Product, pk=id_product)
        if product.count == 0:
            log.info("Товар с id %s отсутствует на складе" % id_product)
            return Response(
                {"message": "The product is out of stock"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart.add(product=product, quantity=count_product)

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

    def get(self, request):
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

    def delete(self, request):
        id_product = int(request.data.get("id"))
        count_product = int(request.data.get("count"))
        log.info(
            "Удаление из корзины продукта с id %s в количестве %s"
            % (id_product, count_product)
        )
        cart = Cart(request)
        cart.remove(id_product, count_product)

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
