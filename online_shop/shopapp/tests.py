import json
from django.test import TestCase
from django.urls import reverse
from django.db.models import Count
from django.contrib.auth.models import User

from .models import Product


class ProductTestCase(TestCase):
    fixtures = ["data.json"]

    def test_get_tags(self):
        """
        Тестирование выгрузки тэгов
        """
        data = {"category": 3}
        response = self.client.get(reverse("api:tags"), data)
        find_data = {"id": 1, "name": "ноутбук"}
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn(find_data, received_data)

    def test_get_categories(self):
        """
        Тестирование выгрузки категорий
        """
        response = self.client.get(reverse("api:categories"))
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_data[0]["title"], "Компьютеры и ноутбуки")

    def test_get_sales(self):
        """
        Тестирование выгрузки скидок
        """
        data = {
            "currentPage": 1,
        }
        response = self.client.get(reverse("api:sales"), data)
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(received_data["items"]), 2)

    def test_get_banners(self):
        """
        Тестирование выгрузки товаров на банер (количество подкатегорий с товарами)
        """
        response = self.client.get(reverse("api:banners"))
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(received_data), 6)


class ProductSortedTestCase(TestCase):
    fixtures = ["data.json"]

    def test_get_catalog_price(self):
        """
        Тестирование выгрузка товаров по цене до 100000 рублей
        """
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 100000,
            "filter[freeDelivery]": "false",
            "filter[available]": "false",
            "category": 4,
            "sort": "price",
            "sortType": "inc",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)

        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(received_data["items"]), 1)
        self.assertEqual(received_data["items"][0]["price"], "19990.00")

    def test_get_catalog_price_to_down(self):
        """
        Тестирование выгрузка товаров и сортировка по убыванию цены
        """
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 500000,
            "filter[freeDelivery]": "false",
            "filter[available]": "false",
            "category": 4,
            "sort": "price",
            "sortType": "inc",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)

        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            float(received_data["items"][0]["price"])
            > float(received_data["items"][1]["price"])
        )

    def test_get_catalog_price_to_up(self):
        """
        Тестирование выгрузка товаров и сортировка по возрастанию цены
        """
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 500000,
            "filter[freeDelivery]": "false",
            "filter[available]": "false",
            "category": 4,
            "sort": "price",
            "sortType": "dec",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)

        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            float(received_data["items"][0]["price"])
            < float(received_data["items"][1]["price"])
        )

    def test_get_catalog_rating_to_up(self):
        """
        Тестирование выгрузка товаров и сортировка по возрастанию рейтинга
        """
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 500000,
            "filter[freeDelivery]": "false",
            "filter[available]": "false",
            "category": 4,
            "sort": "rating",
            "sortType": "dec",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_data["items"][0]["rating"], 0)
        self.assertEqual(received_data["items"][1]["rating"], 3.0)

    def test_get_catalog_rating_to_down(self):
        """
        Тестирование выгрузка товаров и сортировка по убыванию рейтинга
        """
        # ToDo перепроверить
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 500000,
            "filter[freeDelivery]": "false",
            "filter[available]": "false",
            "category": 4,
            "sort": "rating",
            "sortType": "inc",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)

        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_data["items"][0]["rating"], 3.0)
        self.assertEqual(received_data["items"][1]["rating"], 0)

    def test_get_catalog_reviews_to_down(self):
        """
        Тестирование выгрузка товаров и сортировка по убыванию количества отзывов
        """
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 500000,
            "filter[freeDelivery]": "false",
            "filter[available]": "false",
            "category": 4,
            "sort": "reviews",
            "sortType": "inc",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)

        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_data["items"][0]["reviews"], 1)
        self.assertEqual(received_data["items"][1]["reviews"], 0)

    def test_get_catalog_reviews_to_up(self):
        """
        Тестирование выгрузка товаров и сортировка по возрастанию количества отзывов
        """
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 500000,
            "filter[freeDelivery]": "false",
            "filter[available]": "false",
            "category": 4,
            "sort": "reviews",
            "sortType": "dec",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_data["items"][0]["reviews"], 0)
        self.assertEqual(received_data["items"][1]["reviews"], 1)

    def test_get_catalog_date_to_up(self):
        """
        Тестирование выгрузка товаров и сортировка по новизне товара (возрастанию)
        """
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 500000,
            "filter[freeDelivery]": "false",
            "filter[available]": "false",
            "category": 4,
            "sort": "date",
            "sortType": "dec",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            received_data["items"][0]["date"] < received_data["items"][1]["date"]
        )

    def test_get_catalog_date_to_down(self):
        """
        Тестирование выгрузка товаров и сортировка по новизне товара (убыванию)
        """
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 500000,
            "filter[freeDelivery]": "false",
            "filter[available]": "false",
            "category": 4,
            "sort": "date",
            "sortType": "inc",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            received_data["items"][0]["date"] > received_data["items"][1]["date"]
        )

    def test_get_catalog_available(self):
        """
        Тестирование выгрузка товаров по наличию
        """
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 500000,
            "filter[freeDelivery]": "false",
            "filter[available]": "true",
            "category": 4,
            "sort": "price",
            "sortType": "inc",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(received_data["items"]), 1)
        self.assertEqual(received_data["items"][0]["price"], "139990.00")

    def test_get_catalog_free_delivery(self):
        """
        Тестирование выгрузка товаров по наличию бесплатной доставки
        """
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 500000,
            "filter[freeDelivery]": "true",
            "filter[available]": "false",
            "category": 4,
            "sort": "price",
            "sortType": "inc",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(received_data["items"]), 1)
        self.assertEqual(received_data["items"][0]["price"], "139990.00")

    def test_get_catalog_tags(self):
        """
        Тестирование выгрузка тегов каталога
        """
        data = {
            "currentPage": 1,
            "filter[name]": 0,
            "filter[minPrice]": 0,
            "filter[maxPrice]": 500000,
            "filter[freeDelivery]": "true",
            "filter[available]": "false",
            "category": 4,
            "sort": "price",
            "sortType": "inc",
            "limit": 20,
        }

        response = self.client.get(reverse("api:catalog"), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(received_data["items"]), 1)
        self.assertIn("AMOLED", received_data["items"][0]["tags"][0]["name"])


class ProductReviewCase(TestCase):
    fixtures = ["data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user: User = User.objects.create_user(
            username="TestUser",
            password="1qaz!QAZ",
            first_name="Алексей Иванов",
            email="alex@shop.com",
        )
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def test_reviews_unauthorized_user(self):
        """
        Тестирование создания отзыва о товаре (пользователь не авторизован)
        """
        data = {
            "text": "Отличный телефон с прекрасными характеристиками",
            "rate": 5,
        }

        response = self.client.post(reverse("api:product_reviews", args=("4",)), data)
        received_data = json.loads(response.content)

        self.assertEqual(response.status_code, 403)

    def test_reviews_authorized_user(self):
        """
        Тестирование создания отзыва о товаре (пользователь авторизован)
        """
        self.client.force_login(self.user)
        data = {
            "text": "Отличный телефон с прекрасными характеристиками",
            "rate": 5,
        }

        count_product_before = Product.objects.filter(pk=4).aggregate(
            Count("reviews__id")
        )

        response = self.client.post(reverse("api:product_reviews", args=("4",)), data)
        received_data = json.loads(response.content)

        count_product_after = Product.objects.filter(pk=4).aggregate(
            Count("reviews__id")
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(received_data["message"], "The review has been created")
        self.assertTrue(
            count_product_after["reviews__id__count"]
            > count_product_before["reviews__id__count"]
        )
