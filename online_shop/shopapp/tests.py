import json
from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User

from .models import Product, Tag


class TagsTestCase(TestCase):
    fixtures = ["data.json"]

    def test_get_tags(self):
        """
        Тестирование выгрузки тэгов
        """
        data = {"category": 1}
        response = self.client.post(reverse("api:tags"), data)
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(received_data["message"], "ok")
