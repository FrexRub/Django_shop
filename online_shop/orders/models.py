from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

from shopapp.models import Product


class DeliveryType(models.TextChoices):
    FREE = "free"
    ORDINARY = "ordinary"
    EXPRESS = "express"


class PaymenType(models.TextChoices):
    ONLINE = "online"
    SOMEONE = "someone"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Заказчик",
        related_name="orders",
    )
    delivery_type = models.CharField(
        max_length=8,
        null=False,
        choices=DeliveryType.choices,
        default=DeliveryType.FREE,
        verbose_name="Тип доставки",
    )
    paymen_type = models.CharField(
        max_length=7,
        null=False,
        choices=PaymenType.choices,
        default=PaymenType.ONLINE,
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
        max_length=15, null=False, default="accepted", verbose_name="Статус заказа"
    )
    city = models.CharField(max_length=40, null=False, blank=True, verbose_name="Город")
    address = models.CharField(
        max_length=150, null=False, blank=True, verbose_name="Адрес доставки"
    )
    products = models.ManyToManyField(
        Product, related_name="orders", verbose_name="Товары"
    )
