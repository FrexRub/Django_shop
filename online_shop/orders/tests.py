import json
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.conf import settings

from shopapp.models import Product


class OrderTestCase(TestCase):
    fixtures = ["data.json"]

    def test_create_order(self):
        """
        Тест создание ордера
        """
        id_product = 1
        count_product = 2

        product_id = str(id_product)
        product: Product = get_object_or_404(Product, pk=id_product)

        session = self.client.session
        cart = session[settings.CART_SESSION_ID] = {}
        cart[product_id] = {"quantity": count_product, "price": str(product.price)}
        session.save()

        response = self.client.post(reverse("api:orders"))

        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(received_data["orderId"], 3)
