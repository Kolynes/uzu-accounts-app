from django.test import TestCase
from . import models
import json
from django.core import mail

class SendVerificationCodeViewTestCase(TestCase):
    def test_send_mode_response(self):
        self.user = models.User.objects.create_user(username="Kolynes", password="password")
        self.user.save()
        response = self.client.post("/send-verification-code/", data={"username": "Kolynes", "mode": "send"})
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        first = str(self.user.verification.code)
        self.assertEqual(json_response["status"], True)
        response = self.client.post("/send-verification-code/", data={"username": "Kolynes", "mode": "send"})
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response["status"], True)
        self.user.refresh_from_db()
        second = self.user.verification.code
        self.assertNotEqual(first, second)
    
    def test_resend_mode_response(self):
        self.user = models.User.objects.create_user(username="Kolynes", password="password")
        response = self.client.post("/send-verification-code/", data={"username": "Kolynes", "mode": "resend"})
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        first = self.user.verification.code
        self.assertEqual(json_response["status"], True)
        response = self.client.post("/send-verification-code/", data={"username": "Kolynes", "mode": "resend"})
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response["status"], True)
        self.user.refresh_from_db()
        second = self.user.verification.code
        self.assertEqual(first, second)

    def test_invalid_username_response(self):
        response = self.client.post("/send-verification-code/", data={"username": "James"})
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response["status"], False)
        self.assertEqual(json_response["error"], "Account not found")


class VerifyViewTestCase(TestCase):
    def test_true_response(self):
        user = models.User.objects.create_user(username="Kolynes", password="password")
        verification = models.Verification.objects.create(user=user, code="1234")
        response = self.client.post("/verify-code/", data={"username": "Kolynes", "code": verification.code})
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response["status"], True)

    def test_false_response(self):
        user = models.User.objects.create_user(username="Kolynes", password="password")
        verification = models.Verification.objects.create(user=user, code="1234")
        response = self.client.post("/verify-code/", data={"username": "Kolynes", "code": "123"})
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response["status"], False)
        self.assertEqual(json_response["error"], "Incorrect verification code.")


class ResetPasswordViewTestCase(TestCase):
    def test_true_response(self):
        user = models.User.objects.create_user(username="Kolynes", password="password")
        verification = models.Verification.objects.create(user=user, code="1234")
        response = self.client.post("/reset-password/", data={"username": "Kolynes", "code": "1234", "new_password": "1234"})
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response["status"], True)


class SignInViewTestCase(TestCase):
    def test_true_response(self):
        user = models.User.objects.create_user(username="Kolynes", password="password")
        response = self.client.post("/sign-in/", data={"username": "Kolynes", "password": "password"})
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response["status"], True)

