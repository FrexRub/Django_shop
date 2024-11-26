import json
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import get_object_or_404

from shopapp.models import Product


class BasketTestCase(TestCase):
    fixtures = ["data.json"]

    def test_add_product(self):
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
        id_product = 1
        count_product = 2
        data = {"id": id_product, "count": count_product}
        response = self.client.post(reverse("api:basket"), data)
        received_data = json.loads(response.content)

        count_add = received_data[0]["count"]

        data = {"id": id_product, "count": count_product - 1}
        response = self.client.delete(reverse("api:basket"), data)
        # received_data = json.loads(response.content)
        print(response)
        # count_after_delete = received_data[0]["count"]

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(count_add - count_after_delete, count_product - 1)
