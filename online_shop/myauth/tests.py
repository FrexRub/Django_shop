import json
from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User

from .models import Profile


class UserRegistrationViewTestCase(TestCase):
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
        # profile: Profile = Profile.objects.select_related("user").filter(user__username="TestUser1").first()
        # print("profile:", profile.user.username, "phone_number: ", profile.phone_number, "email: ", profile.user.email)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            User.objects.filter(username="TestUser1").exists()
        )
        self.assertTrue(
            Profile.objects.select_related("user").filter(user__username="TestUser1").exists()
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


class UserLoginViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user: User = User.objects.create_user(
            username="TestUser",
            password="1qaz!QAZ"
        )
        cls.user.save()

        # cls.profile: Profile = Profile.objects.create(user=cls.user)
        # cls.profile.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        # cls.profile.delete()

    def test_login_user_ok(self):
        """
        Тестирование входа пользователя в личный кабинет
        """
        user = {
            "username": "TestUser",
            "password": "1qaz!QAZ"
        }
        response = self.client.post(reverse("api:sign_in"), user)
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_data["message"], "User login successfully")

    def test_login_user_no_user(self):
        """
        Тестирование входа пользователя в личный кабинет (полльзователь не зарегистрирован)
        """
        user = {
            "username": "TestUser10",
            "password": "1qaz!QAZ"
        }
        response = self.client.post(reverse("api:sign_in"), user)
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(received_data["detail"], "No such user")

    def test_login_user_bad_password(self):
        """
        Тестирование входа пользователя в личный кабинет (не верный пароль)
        """
        user = {
            "username": "TestUser",
            "password": "123456"
        }
        response = self.client.post(reverse("api:sign_in"), user)
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(received_data["message"], "Invalid password")
