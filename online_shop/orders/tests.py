import json
from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.conf import settings

from shopapp.models import Product
from orders.models import Order


class OrderTestCase(TestCase):
    fixtures = ["data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = Client()

        id_product = 1
        count_product = 2
        product_id = str(id_product)
        product: Product = get_object_or_404(Product, pk=id_product)

        session = cls.client.session
        session[settings.CART_SESSION_ID] = {}
        session[settings.CART_SESSION_ID][product_id] = {
            "quantity": count_product,
            "price": str(product.price),
        }
        session.save()

    @classmethod
    def tearDownClass(cls):
        cls.client.session.flush()


    # def setUp(self):
    #     self.client = Client()
    #
    #     id_product = 1
    #     count_product = 2
    #     product_id = str(id_product)
    #     product: Product = get_object_or_404(Product, pk=id_product)
    #
    #     session = self.client.session
    #     session[settings.CART_SESSION_ID] = {}
    #     session[settings.CART_SESSION_ID][product_id] = {
    #         "quantity": count_product,
    #         "price": str(product.price),
    #     }
    #     session.save()

    # def tearDown(self):
    #     self.client.session.flush()

    def test_create_order(self):
        """
        Тест создание ордера
        """
        response = OrderTestCase.client.post(reverse("api:orders"))
        received_data = json.loads(response.content)

        print("received_data", received_data)

        order: Order = get_object_or_404(Order, pk=received_data["orderId"])

        self.assertEqual(response.status_code, 201)
        self.assertEqual(received_data["orderId"], 3)
        self.assertEqual(order.status, "created")

    def test_get_order_id(self):
        """
        Тест получения ордера по id
        """
        response = OrderTestCase.client.post(reverse("api:orders"))
        received_data = json.loads(response.content)

        response = OrderTestCase.client.get(reverse("api:orders_details", args=(received_data["orderId"],)))
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Apple IPhone 13", received_data["products"][1]["title"])

    def test_post_order_id(self):
        """
        Тест редактирования ордера по id
        """
        data = {
            "deliveryType": "ordinary",
            "paymentType": "online",
            "city": "Moscow",
            "address": "ul. Mira, dom 10",
        }

        response = OrderTestCase.client.post(reverse("api:orders"))
        received_data = json.loads(response.content)

        response = OrderTestCase.client.post(reverse("api:orders_details", args=(received_data["orderId"],)), data)
        received_data = json.loads(response.content)

        order: Order = get_object_or_404(Order, pk=received_data["orderId"])

        self.assertEqual(response.status_code, 201)
        self.assertEqual(order.address, "ul. Mira, dom 10")

    def test_pyment_order_id(self):
        """
        Тест оплаты ордера по id (без ошибок)
        """
        data = {
            "name": "Lena Lee",
            "number": "9999999999999999",
            "year": "23",
            "month": "11",
            "code": "123",
        }

        response = OrderTestCase.client.post(reverse("api:orders"))
        received_data = json.loads(response.content)
        order_id = received_data["orderId"]

        response = OrderTestCase.client.post(reverse("api:payment", args=(order_id,)), data)
        received_data = json.loads(response.content)

        order: Order = get_object_or_404(Order, pk=order_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_data["message"], "Данные указаны верно")
        self.assertEqual(order.status, "paid")


    def test_pyment_err_number(self):
        """
        Тест оплаты ордера по id (ошибка в номере карты)
        """
        data = {
            "name": "Lena Lee",
            "number": "9999-9999-9999-9999",
            "year": "23",
            "month": "11",
            "code": "123",
        }

        response = OrderTestCase.client.post(reverse("api:orders"))
        received_data = json.loads(response.content)
        order_id = received_data["orderId"]

        response = OrderTestCase.client.post(reverse("api:payment", args=(order_id,)), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(received_data["message"], "Счёт указано не верно")

    def test_pyment_err_year(self):
        """
        Тест оплаты ордера по id (ошибка в году)
        """
        data = {
            "name": "Lena Lee",
            "number": "9999999999999999",
            "year": "234",
            "month": "11",
            "code": "123",
        }

        response = OrderTestCase.client.post(reverse("api:orders"))
        received_data = json.loads(response.content)
        order_id = received_data["orderId"]

        response = OrderTestCase.client.post(reverse("api:payment", args=(order_id,)), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(received_data["message"], "Год указан не верно")

    def test_pyment_err_month(self):
        """
        Тест оплаты ордера по id (ошибка в месяце)
        """
        data = {
            "name": "Lena Lee",
            "number": "9999999999999999",
            "year": "23",
            "month": "14",
            "code": "123",
        }

        response = OrderTestCase.client.post(reverse("api:orders"))
        received_data = json.loads(response.content)
        order_id = received_data["orderId"]

        response = OrderTestCase.client.post(reverse("api:payment", args=(order_id,)), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(received_data["message"], "Месяц указан не верно")

    def test_pyment_err_code(self):
        """
        Тест оплаты ордера по id (ошибка в коде)
        """
        data = {
            "name": "Lena Lee",
            "number": "9999999999999999",
            "year": "23",
            "month": "11",
            "code": "1234",
        }

        response = OrderTestCase.client.post(reverse("api:orders"))
        received_data = json.loads(response.content)
        order_id = received_data["orderId"]

        response = OrderTestCase.client.post(reverse("api:payment", args=(order_id,)), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(received_data["message"], "Код указан не верно")

    def test_pyment_err_name(self):
        """
        Тест оплаты ордера по id (ошибка в имени)
        """
        data = {
            "name": "Lena Lee12",
            "number": "9999999999999999",
            "year": "23",
            "month": "11",
            "code": "123",
        }

        response = OrderTestCase.client.post(reverse("api:orders"))
        received_data = json.loads(response.content)
        order_id = received_data["orderId"]

        response = OrderTestCase.client.post(reverse("api:payment", args=(order_id,)), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(received_data["message"], "Имя указано не верно")