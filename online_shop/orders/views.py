import logging
from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiExample,
)

from basket.cart import Cart
from shopapp.models import Product
from orders.models import Order, OrderInfoBasket
from orders.serializers import OrderSerializer

log = logging.getLogger(__name__)


class OrderApiView(APIView):
    def post(self, request):
        log.info("Начало выполнения запроса по созданию ордера")
        cart = Cart(request)
        user: User = self.request.user

        list_id = cart.list_id_products()

        if len(list_id) == 0:
            return Response(
                {"message": "The basket is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        products = Product.objects.filter(id__in=list_id)

        total_cost = 0
        for i_id in list_id:
            product_from_basket = cart.get(i_id)
            total_cost += Decimal(product_from_basket["quantity"]) * Decimal(product_from_basket["price"])

        order = Order.objects.create(
            user=user,
            total_cost=total_cost,
        )

        for product in products:
            product_from_basket = cart.get(product.pk)
            m2m_order = OrderInfoBasket(
                order=order,
                product=product,
                count_in_order=product_from_basket["quantity"],
                price_in_order=product_from_basket["price"]
            )

        m2m_order.save()

        return Response(
            {"orderId": order.pk},
            status=status.HTTP_201_CREATED,
        )


class OrderDetailApiView(APIView):
    def get(self, request, pk: int):
        order = (
            Order.objects.filter(pk=pk)
            .select_related("user")
            .prefetch_related("basket", "user__profile")
            .order_by("id")
        )

        serializer = OrderSerializer(order, many=True, context={"request": request})

        print(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
