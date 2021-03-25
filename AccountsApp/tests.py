from django.test import TestCase
from . import models
import json
from django.core import mail

class SendVerificationCodeViewTestCase(TestCase):
    def test_send_mode_response(self):
        self.user = models.User.objects.create_user(username="Kolynes", password="password")
        self.user.save()
        response = self.client.post("/send_verification_code/", data={"username": "Kolynes", "mode": "send"})
        self.assertEqual(response.status_code, 200)
        first = str(self.user.verification.code)
        response = self.client.post("/send_verification_code/", data={"username": "Kolynes", "mode": "send"})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        second = self.user.verification.code
        self.assertNotEqual(first, second)
    
    def test_resend_mode_response(self):
        self.user = models.User.objects.create_user(username="Kolynes", password="password")
        response = self.client.post("/send_verification_code/", data={"username": "Kolynes", "mode": "resend"})
        self.assertEqual(response.status_code, 200)
        first = self.user.verification.code
        response = self.client.post("/send_verification_code/", data={"username": "Kolynes", "mode": "resend"})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        second = self.user.verification.code
        self.assertEqual(first, second)


class VerifyViewTestCase(TestCase):
    def test_true_response(self):
        user = models.User.objects.create_user(username="Kolynes", password="password")
        verification = models.Verification.objects.create(user=user, code="1234")
        response = self.client.post("/verify_code/", data={"username": "Kolynes", "code": verification.code})
        self.assertEqual(response.status_code, 200)

    def test_false_response(self):
        user = models.User.objects.create_user(username="Kolynes", password="password")
        verification = models.Verification.objects.create(user=user, code="1234")
        response = self.client.post("/verify_code/", data={"username": "Kolynes", "code": "123"})
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.content)


class ResetPasswordViewTestCase(TestCase):
    def test_true_response(self):
        user = models.User.objects.create_user(username="Kolynes", password="password")
        verification = models.Verification.objects.create(user=user, code="1234")
        response = self.client.post("/reset_password/", data={"username": "Kolynes", "code": "1234", "new_password": "1234"})
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, 200)


class SignInViewTestCase(TestCase):
    def test_true_response(self):
        user = models.User.objects.create_user(username="Kolynes", password="password")
        response = self.client.post("/sign_in/", data={"username": "Kolynes", "password": "password"})
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

