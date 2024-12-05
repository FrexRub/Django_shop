import logging
from decimal import Decimal
import time

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)

from basket.cart import Cart
from shopapp.models import Product, Specification
from orders.models import Order, OrderInfoBasket, StatusType, DeliveryType
from orders.serializers import (
    OrderSerializer,
    OrderIdSerializer,
    OrderUpdateSerializer,
    PaymentSerializer,
    PaymentResultSerializer,
)
from shopapp.serializers import ProductShortSerializer
from services.payment import checking_payments
from orders.tasks import send_email_about_order_created

log = logging.getLogger(__name__)


class OrderApiView(APIView):
    @extend_schema(
        tags=["order"],
        summary="Вывод списка ордеров пользователя",
        responses={
            status.HTTP_200_OK: OrderSerializer(many=True),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            ),
        },
    )
    def get(self, request):
        """
        Генерирует список заказов пользователя
        """
        orders = (
            Order.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("basket", "user__profile")
            .order_by("-created_at")
        )

        orders_list = list()
        for order in orders:
            serializer = OrderSerializer(order, context={"order": order})
            orders_list.append(serializer.data)

        return Response(
            orders_list,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["order"],
        summary="Создание заказа",
        request=ProductShortSerializer(many=True),
        responses={
            status.HTTP_200_OK: OrderIdSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            ),
        },
    )
    def post(self, request):
        """
        Создается ордер из товаров в корзине
        """
        log.info("Начало выполнения запроса по созданию ордера")
        cart = Cart(request)

        if request.user.is_authenticated:
            user: User = self.request.user
        else:
            user = get_object_or_404(User, pk=1)

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
            total_cost += Decimal(product_from_basket["quantity"]) * Decimal(
                product_from_basket["price"]
            )

        order = Order.objects.create(
            user=user,
            total_cost=total_cost,
        )

        free_delivery = True
        for product in products:
            free_delivery &= product.freeDelivery
            product_from_basket = cart.get(product.pk)
            m2m_order = OrderInfoBasket.objects.create(
                order=order,
                product=product,
                count_in_order=product_from_basket["quantity"],
                price_in_order=product_from_basket["price"],
            )

        delivery: Product = Product.objects.filter(title="Доставка").first()
        specifications: Specification = Specification.objects.filter(
            product=delivery, name="Сумма заказа"
        ).first()

        if not free_delivery and Decimal(total_cost) < Decimal(specifications.value):
            log.info("Добавление в ордер id%s стоимость доставки" % order.pk)
            m2m_order = OrderInfoBasket.objects.create(
                order=order,
                product=delivery,
                count_in_order=1,
                price_in_order=delivery.price,
            )
            order.total_cost += Decimal(delivery.price)
            order.save()

        else:
            delivery_free: Product = Product.objects.filter(
                title="Бесплатная доставка"
            ).first()
            m2m_order = OrderInfoBasket.objects.create(
                order=order,
                product=delivery_free,
                count_in_order=1,
                price_in_order=delivery_free.price,
            )

        log.info("Новый ордер с %s создан, статус ордера %s" % (order.pk, order.status))

        return Response(
            {"orderId": order.pk},
            status=status.HTTP_201_CREATED,
        )


class OrderDetailApiView(APIView):
    @extend_schema(
        tags=["order"],
        summary="Информация о заказе по id",
        responses={
            status.HTTP_200_OK: OrderSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            ),
        },
    )
    def get(self, request, pk: int):
        """
        Вывод данных о заказе по id
        :param request:
        :param pk: int
        Номер ордера
        :return:
        """
        order = (
            Order.objects.filter(pk=pk)
            .select_related("user")
            .prefetch_related("basket", "user__profile")
            .first()
        )

        if request.user.is_authenticated and (order.user.id == 1):
            order.user = self.request.user
            order.save()

        serializer = OrderSerializer(order, context={"order": order})

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["order"],
        summary="Редактирование заказа по id",
        request=OrderUpdateSerializer,
        responses={
            status.HTTP_201_CREATED: OrderIdSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            ),
        },
    )
    def post(self, request, pk: int):
        """
        Редактирование заказа с заданным id
        :param request:
        :param pk: int
        Номер ордера
        :return:
        """
        order = (
            Order.objects.filter(pk=pk)
            .select_related("user")
            .prefetch_related("basket", "user__profile")
            .first()
        )

        order.delivery_type = request.data.get("deliveryType")
        order.payment_type = request.data.get("paymentType")
        order.city = request.data.get("city")
        order.address = request.data.get("address")

        order.status = StatusType.ACCEPTED
        order.save()

        if order.delivery_type == DeliveryType.EXPRESS:
            log.info("Добавление в ордер id%s стоимость экспресс-доставки" % order.pk)
            delivery: Product = get_object_or_404(Product, title="Экспресс-доставка")
            m2m_order = OrderInfoBasket.objects.create(
                order=order,
                product=delivery,
                count_in_order=1,
                price_in_order=delivery.price,
            )
            m2m_order.save()
            order.total_cost += Decimal(delivery.price)
            order.save()

        log.info("Ордер с %s подтвержден, статус ордера %s" % (order.pk, order.status))

        return Response(
            {"orderId": order.pk},
            status=status.HTTP_201_CREATED,
        )


class PaymentApiView(APIView):
    @extend_schema(
        tags=["payment"],
        summary="Оплата заказа по id",
        request=PaymentSerializer,
        responses={
            status.HTTP_200_OK: PaymentResultSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=None,
                description="Что-то пошло не так",
            ),
        },
        examples=[
            OpenApiExample(
                "Pyment example",
                description="Пример заполнения полей оплаты",
                value={
                    "name": "Lena Lee",
                    "number": "9999999999999999",
                    "year": "23",
                    "month": "11",
                    "code": "123",
                },
                status_codes=[str(status.HTTP_200_OK)],
            )
        ],
    )
    def post(self, request, pk: int):
        """
        Оплата заказа по id
        :param request:
        :param pk: int
        :return:
        """
        log.info("Заполнение данных платежной карты")
        result_check = checking_payments(request)

        if result_check["status"] == status.HTTP_200_OK:
            time.sleep(5)
            order = get_object_or_404(Order, pk=pk)
            order.status = StatusType.PAID
            order.save()
            log.info("Ордер с %s оплачен, статус ордера %s" % (order.pk, order.status))

            log.info(
                "Отправка письма клиенту %s с информацией об ордере с id %s"
                % (order.user.first_name, pk)
            )
            send_email_about_order_created.delay(
                user_name=order.user.first_name, order_id=pk
            )

            cart = Cart(request)
            cart.delete_cart()
            log.info("Карзина с товарами для ордера %s удалена" % order.pk)

        return Response(
            {"message": result_check["massage"]},
            status=result_check["status"],
        )
