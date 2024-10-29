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

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

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


class UserEditProfileViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # Create TestUser1
        cls.user_1: User = User.objects.create_user(
            username="TestUser1",
            password="1qaz!QAZ"
        )
        # cls.user_1.email = "test@shop.com"
        cls.user_1.save()

        cls.profile_1: Profile = Profile.objects.create(user=cls.user_1)
        # cls.profile_1.phone_number = "+73527362875"
        cls.profile_1.save()

        # Create TestUser2
        cls.user_2: User = User.objects.create_user(
            username="TestUser2",
            password="1qaz!QAZ"
        )
        cls.user_2.email = "test@shop.com"
        cls.user_2.save()

        cls.profile_2: Profile = Profile.objects.create(user=cls.user_2)
        cls.profile_2.phone_number = "+73527362875"
        cls.profile_2.save()

    @classmethod
    def tearDownClass(cls):
        cls.user_1.delete()
        cls.profile_1.delete()
        cls.user_2.delete()
        cls.profile_2.delete()

    def test_edit_profile_unauthorized_user(self):
        """
        Тестирование редактирования профиля (пользователь не авторизован)
        """
        data_profile = {
            "fullName": "Алексей Иванов",
            "phone": "+79151232358",
            "email": "alex@shop.com",
        }
        response = self.client.post(reverse("api:profile"), data_profile)

        self.assertEqual(response.status_code, 403)

    def test_edit_profile(self):
        """
        Тестирование редактирования профиля
        """
        self.client.force_login(self.user_1)
        data_profile = {
            "fullName": "Алексей Иванов",
            "phone": "+79151232358",
            "email": "alex@shop.com",
        }

        response = self.client.post(reverse("api:profile"), data_profile)
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_data["message"], "User registered successfully")
        self.assertTrue(
            User.objects.filter(first_name="Алексей Иванов").exists()
        )
        self.assertTrue(
            User.objects.filter(email="alex@shop.com").exists()
        )
        self.assertTrue(
            Profile.objects.filter(phone_number="+79151232358").exists()
        )

    def test_edit_profile_email(self):
        """
        Тестирование редактирования профиля (повторение почты)
        """
        self.client.force_login(self.user_1)
        data_profile = {
            "fullName": "Алексей Иванов",
            "phone": "+79151232358",
            "email": "test@shop.com",
        }

        response = self.client.post(reverse("api:profile"), data_profile)
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(received_data["message"], "Email in use")

    def test_edit_profile_phone_bad(self):
        """
        Тестирование редактирования профиля (неверный формат номера телефона)
        """
        self.client.force_login(self.user_1)
        data_profile = {
            "fullName": "Алексей Иванов",
            "phone": "+234",
            "email": "alex@shop.com",
        }

        response = self.client.post(reverse("api:profile"), data_profile)
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(received_data["phone"][0], "Invalid phone")

    def test_edit_profile_phone(self):
        """
        Тестирование редактирования профиля (повторение телефона)
        """
        self.client.force_login(self.user_1)
        data_profile = {
            "fullName": "Алексей Иванов",
            "phone": "+73527362875",
            "email": "alex@shop.com",
        }

        response = self.client.post(reverse("api:profile"), data_profile)
        received_data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(received_data["message"], "Phone in use")
