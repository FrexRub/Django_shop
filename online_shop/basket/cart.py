from typing import Any
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from django.conf import settings

from shopapp.models import Product, Sales

log = logging.getLogger(__name__)


class Cart(object):

    def __init__(self, request):
        """
        Инициализация корзины
        """
        self.session = request.session

        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            log.info("Инициализация корзины товаров")
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def add(self, product: Product, quantity: int = 1):
        """
        Добавить продукт в корзину или обновить его количество.
        :param product: Product
            добавляемый продукт в корзину
        :param quantity: int
            количество добавляемого продукта
        :return: None
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}

            # search discount for product
            date_now = datetime.now(tz=ZoneInfo(settings.TIME_ZONE))
            product_discount = Sales.objects.filter(product=product).first()

            if product_discount and (
                product_discount.dateFrom <= date_now <= product_discount.dateTo
            ):
                log.info(
                    "У товара с id%s цена со скидкой %s"
                    % (product_id, product_discount.salePrice)
                )
                self.cart[product_id]["price"] = str(product_discount.salePrice)

        self.cart[product_id]["quantity"] += quantity
        self.save()

    def save(self):
        """
        Сохранение изменений в текущей сессии
        :return: None
        """
        # Обновление сессии cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, id: int, quantity: int):
        """
        Удаление товара из корзины.
        :param id: int
            id продукта удаляемого из корзины
        :param quantity: int
            количество удаляемых из корзины продуктов
        :return:
        """
        product_id = str(id)
        if product_id in self.cart:
            # del self.cart[product_id]
            if self.cart[product_id]["quantity"] > quantity:
                self.cart[product_id]["quantity"] -= quantity
            else:
                del self.cart[product_id]

            self.save()

        if len(self.list_id_products()) == 0:
            self.delete_cart()

    def list_id_products(self) -> list[str]:
        """
        Возвращает список id товаров в корзине
        :return: list[str]
        """
        return list(self.cart.keys())

    def get(self, id: int) -> dict[str, Any]:
        """
        Возвращает данные о продукте в корзине по его id
        :param id:int
            id продукта
        :return: dict[str, Any]
        """
        product_id = str(id)
        return self.cart[product_id]

    def delete_cart(self):
        log.info("Удаление корзины товаров")
        del self.session[settings.CART_SESSION_ID]
