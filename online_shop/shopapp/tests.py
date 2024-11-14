import json
from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User

from .models import Product, Tag


class ProductTestCase(TestCase):
    fixtures = ["data.json"]

    def test_get_tags(self):
        """
        Тестирование выгрузки тэгов
        """
        data = {"category": 1}
        response = self.client.get(reverse("api:tags"), data)
        find_data = {"id": 2, "name": "ноутбук"}
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn(find_data, received_data)

    def test_get_categories(self):
        """
        Тестирование выгрузки категорий
        """
        response = self.client.get(reverse("api:categories"))
        find_data = {"id": 2, "name": "ноутбук"}
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_data[0]["title"], "Компьютеры и ноутбуки")

    # catalog/?filter[name]=&filter[minPrice]=0&filter[maxPrice]=500000&filter[freeDelivery]=false
    # &filter[available]=true&currentPage=1&category=2&sort=price&sortType=inc&limit=20
    def test_get_catalog(self):
        """
        Тестирование выгрузка товаров по фильтру
        """
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 100000,
            "filter[freeDelivery]": "false",
            "filter[available]": "false",
            "category": 2,
            "sort": "price",
            "sortType": "inc",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)

        received_data = json.loads(response.content)
        print(received_data)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(received_data[0]["title"], "Компьютеры и ноутбуки")
