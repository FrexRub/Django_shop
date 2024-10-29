import json
from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User


class UserViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user: User = User.objects.create_user(
            username="TestUser",
            password="1qaz!QAZ"
        )
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_registration_user_bad_password(self):
        """
        Тестирование на надежность пароля
        """
        user = {
            "username": "TestUser1",
            "password": "123456"
        }
        response = self.client.post(reverse("api:sign_up"), user)
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(received_data["password"][0], "Invalid password")

    def test_registration_user(self):
        """
        Тестирование на регистрацию пользователя
        """
        user = {
            "username": "TestUser1",
            "password": "1qaz!QAZ"
        }
        response = self.client.post(reverse("api:sign_up"), user)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            User.objects.filter(username="TestUser1").exists()
        )

    def test_registration_user_again(self):
        """
        Тестирование на регистрацию пользователя повторно
        """
        user = {
            "username": "TestUser",
            "password": "1qaz!QAZ"
        }
        response = self.client.post(reverse("api:sign_up"), user)
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(received_data["message"], "Username is already in use")
