from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Verification(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	code = models.CharField(max_length=settings.ACCOUNTS_APP["code_length"])
	username_signature = models.TextField(null=True)
	code_signature = models.TextField(null=True)
	verified = models.BooleanField(default=False)
	recovery = models.BooleanField(default=True)
