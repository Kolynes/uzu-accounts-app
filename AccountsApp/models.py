from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from .utils.code_generator import generate_number_code
from datetime import timedelta
from django.utils import timezone
from django.core.signing import TimestampSigner, SignatureExpired

User = get_user_model()

class Verification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=settings.ACCOUNTS_APP["code_length"])
    username_signature = models.TextField(null=True)
    code_signature = models.TextField(null=True)
    verified = models.BooleanField(default=False)
    recovery = models.BooleanField(default=True)

class TwoFactorTokens(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(
        max_length=settings.ACCOUNTS_APP["code_length"])
    signature = models.TextField(null=True, db_index=True)

    @classmethod
    def Find(cls, signature, code):
        return cls.objects.get(
            models.Q(signature=signature) & models.Q(code=code)
        )
    @property
    def code_length(self):
        return int(settings.ACCOUNTS_APP["code_length"])

    def save(self, *args, **kwargs):
        if not self.code:
            self.__generate_data()
        super().save(*args, **kwargs)
    
    def __generate_data(self):
        self.signature = TimestampSigner().sign(self.user.get_username())
        self.code = generate_number_code(self.code_length)

    def is_expired(self):
        duration = settings.ACCOUNTS_APP["2fa_duration"]
        max_age = timedelta(minutes=duration)
        try:
            TimestampSigner().unsign(self.signature, max_age=max_age)
        except SignatureExpired:
            return True
        return False
        
