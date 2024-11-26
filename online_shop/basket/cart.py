from decimal import Decimal
from django.conf import settings
from shopapp.models import Product


class Cart(object):

    def __init__(self, request):
        """
        Инициализация корзины
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product: Product, quantity: int = 1, update_quantity: bool = False):
        """
        Добавить продукт в корзину или обновить его количество.
        :param product: Product
            добавляемый продукт в корзину
        :param quantity: int
            количество добавляемого продукта
        :param update_quantity: bool
            статус обновления количества продукта
        :return:
        """
        # ToDo add sales
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}

        if update_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
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

    def list_id_products(self):
        return list(self.cart.keys())

    def get(self, id: int):
        product_id = str(id)
        return self.cart[product_id]
