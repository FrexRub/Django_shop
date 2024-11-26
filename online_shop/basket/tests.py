import json
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Product


class BasketTestCase(TestCase):
    fixtures = ["data.json"]

    def test_add_product(self):
        data = {"id": 1, "count": 1}
        response = self.client.post(reverse("api:basket"), data)
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(received_data[0]["price"], "67399.00")
