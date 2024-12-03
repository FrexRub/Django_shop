import json
from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.conf import settings

from shopapp.models import Product
from orders.models import Order


class OrderTestCase(TestCase):
    fixtures = ["data.json"]

    def setUp(self):
        self.client = Client()

        id_product = 1
        count_product = 2
        product_id = str(id_product)
        product: Product = get_object_or_404(Product, pk=id_product)

        session = self.client.session
        session[settings.CART_SESSION_ID] = {}
        session[settings.CART_SESSION_ID][product_id] = {
            "quantity": count_product,
            "price": str(product.price),
        }
        session.save()

    def tearDown(self):
        self.client.session.flush()

    def test_create_order(self):
        """
        Тест создание ордера
        """

        response = self.client.post(reverse("api:orders"))
        received_data = json.loads(response.content)

        order: Order = get_object_or_404(Order, pk=received_data["orderId"])

        self.assertEqual(response.status_code, 201)
        self.assertEqual(received_data["orderId"], 3)
        self.assertEqual(order.status, "created")

    def test_get_order_id(self):
        """
        Тест получения ордера по id
        """

        response = self.client.post(reverse("api:orders"))

        response = self.client.get(reverse("api:orders_details", args=(4,)))
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

        response = self.client.post(reverse("api:orders"))

        response = self.client.post(reverse("api:orders_details", args=(5,)), data)
        received_data = json.loads(response.content)

        order: Order = get_object_or_404(Order, pk=received_data["orderId"])

        self.assertEqual(response.status_code, 201)
        self.assertEqual(received_data["orderId"], 5)
        self.assertEqual(order.address, "ul. Mira, dom 10")
