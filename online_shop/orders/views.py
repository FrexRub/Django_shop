import logging

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
from orders.models import Order

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

        products = (
            Product.objects.filter(id__in=list_id)
            .select_related("category")
            .prefetch_related(
                "tags", "images", "specifications", "reviews",
            )
            .order_by("id")
        )

        total_cost = 0
        for i_id in list_id:
            product_from_basket = cart.get(i_id)
            total_cost += product_from_basket["quantity"] * product_from_basket["price"]

        order = Order.objects.create(
            user=user,
            total_cost=total_cost,
            products=products
        )
        return Response(
            {"orderId": order.pk},
            status=status.HTTP_201_CREATED,
        )
