import json
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import get_object_or_404

from shopapp.models import Product


class BasketTestCase(TestCase):
    fixtures = ["data.json"]

    def test_add_product(self):
        """
        Тест добавления продукта в корзину
        """
        id_product = 1
        count_product = 2
        data = {"id": id_product, "count": count_product}

        product: Product = get_object_or_404(Product, pk=id_product)
        count_product_before = product.count

        response = self.client.post(reverse("api:basket"), data)

        product: Product = get_object_or_404(Product, pk=id_product)
        count_product_after = product.count

        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(received_data[0]["price"], "67399.00")
        self.assertEqual(count_product_before - count_product_after, count_product)

    def test_delete_product(self):
        """
        Тест удаления единицы продукта из корзины
        """
        id_product = 1
        count_product = 2
        data = {"id": id_product, "count": count_product}
        response = self.client.post(reverse("api:basket"), data)
        received_data = json.loads(response.content)

        count_add = received_data[0]["count"]

        data = {"id": id_product, "count": count_product - 1}
        headers = {"Content-Type": "application/json"}
        response = self.client.delete(
            reverse("api:basket"), headers=headers, data=json.dumps(data)
        )
        received_data = json.loads(response.content)
        count_after_delete = received_data[0]["count"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(count_add - count_after_delete, count_product - 1)

    def test_add_product_out_of_stock(self):
        """
        Тест добавления продукта в корзину при его отсутствии на складе
        """
        id_product = 4
        count_product = 1
        data = {"id": id_product, "count": count_product}

        product: Product = get_object_or_404(Product, pk=id_product)
        count_product = product.count

        response = self.client.post(reverse("api:basket"), data)

        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(count_product, 0)
        self.assertEqual(received_data["message"], "The product is out of stock")

    def test_add_product_limit(self):
        """
        Тест добавления продукта в корзину при превышении наличия
        """
        id_product = 5
        count_product = 3
        data = {"id": id_product, "count": count_product}

        product: Product = get_object_or_404(Product, pk=id_product)
        count_product_real = product.count

        response = self.client.post(reverse("api:basket"), data)

        received_data = json.loads(response.content)
        count_in_basket = received_data[0]["count"]

        self.assertEqual(response.status_code, 201)
        self.assertTrue(count_product_real == count_in_basket)
        self.assertTrue(count_product > count_in_basket)
