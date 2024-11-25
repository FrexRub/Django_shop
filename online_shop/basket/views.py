import logging

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .cart import Cart
from shopapp.views import Product
from shopapp.serializers import ProductSerializer

log = logging.getLogger(__name__)


class BasketApiView(APIView):
    def post(self, request):
        id_product = int(request.data.get("id"))
        count_product = int(request.data.get("count"))
        log.info(
            "Добавление в корзину продукта с id %s в количестве %s"
            % (id_product, count_product)
        )
        cart = Cart(request)
        product: Product = get_object_or_404(Product, pk=id_product)
        cart.add(product=product, quantity=count_product, update_quantity=True)

        list_id = cart.list_id_products()
        products = (
            Product.objects.filter(id__in=list_id)
            .select_related("category")
            .prefetch_related(
                "tags", "images", "specifications", "reviews", "reviews__author"
            )
            .order_by("id")
        )
        serializer = ProductSerializer(products, many=True)

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
        serializer = ProductSerializer(products, many=True)
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
        print("!!!!!", cart.list_id_products())
        cart.remove(id_product, count_product)
        print("!!!!!", cart.list_id_products())
        return Response(
            status=status.HTTP_200_OK,
        )
