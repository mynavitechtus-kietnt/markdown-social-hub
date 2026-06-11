"""
accounts/tests/test_views.py — Unit test cho Auth endpoints.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile


class RegisterViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("auth-register")

    def test_register_success(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass@123",
            "password_confirm": "StrongPass@123",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        # Tự động tạo UserProfile
        self.assertTrue(UserProfile.objects.filter(user__username="newuser").exists())

    def test_register_password_mismatch(self):
        data = {
            "username": "newuser2",
            "email": "newuser2@example.com",
            "password": "StrongPass@123",
            "password_confirm": "WrongPass@999",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        User.objects.create_user(username="existing", email="taken@example.com", password="pass")
        data = {
            "username": "newuser3",
            "email": "taken@example.com",
            "password": "StrongPass@123",
            "password_confirm": "StrongPass@123",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="loginuser", password="pass@1234")
        self.url = reverse("auth-login")

    def test_login_success(self):
        response = self.client.post(
            self.url, {"username": "loginuser", "password": "pass@1234"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        response = self.client.post(
            self.url, {"username": "loginuser", "password": "wrongpass"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="profileuser", password="pass@1234")
        UserProfile.objects.create(user=self.user)
        self.url = reverse("auth-profile")

    def test_get_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "profileuser")

    def test_get_profile_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_preferences(self):
        self.client.force_authenticate(user=self.user)
        data = {"preferences": {"theme": "dark", "font_size": 16}}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["preferences"]["theme"], "dark")

    def test_invalid_preferences_theme(self):
        self.client.force_authenticate(user=self.user)
        data = {"preferences": {"theme": "blue"}}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
