from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

from shopapp.models import Product


class DeliveryType(models.TextChoices):
    ORDINARY = "ordinary"
    EXPRESS = "express"


class PaymentType(models.TextChoices):
    ONLINE = "online"
    SOMEONE = "someone"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Покупатель",
        related_name="orders",
    )
    delivery_type = models.CharField(
        max_length=8,
        null=False,
        choices=DeliveryType.choices,
        default=DeliveryType.ORDINARY,
        verbose_name="Тип доставки",
    )
    payment_type = models.CharField(
        max_length=7,
        null=False,
        choices=PaymentType.choices,
        default=PaymentType.ONLINE,
        verbose_name="Способ оплаты",
    )
    total_cost = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Общая цена заказа",
    )
    status = models.CharField(
        max_length=15, verbose_name="Статус заказа"
    )
    city = models.CharField(max_length=40, null=False, blank=True, verbose_name="Город")
    address = models.CharField(
        max_length=80, null=False, blank=True, verbose_name="Адрес доставки"
    )
    basket = models.ManyToManyField(
        Product, through="OrderInfoBasket", verbose_name="Товары из корзины"
    )


class OrderInfoBasket(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name="Заказ",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар",
    )
    count_in_order = models.PositiveSmallIntegerField(
        default=0, verbose_name="Количество товара",
    )
    price_in_order = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Цена",
    )
