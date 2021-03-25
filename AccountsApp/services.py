from django.contrib.auth import get_user_model
from . import models
from utils.shortcuts import json_response
from utils import code_generator
import logging
from django.conf import settings
from django.core import signing
import re
from django.core.mail import send_mail

logger = logging.getLogger("AccountRecoveryApp.views")
UserModel = get_user_model()

def create_verification(request):
    """
        creates a verification object and attaches it to the user
    """
    username = request.POST.get("username")
    if username:
        try:
            user = UserModel.objects.get(**{
                UserModel.USERNAME_FIELD: username
            })
        except UserModel.DoesNotExist:
            return json_response(404, error={
                "summary": "Account not found"
            })
    else:
        user = request.user
    verification, created = models.VerificationModel.objects.get_or_create(user=user)
    if created or not verification.username_signature:
        verification.username_signature = signing.Signer().signature(user.get_username())
    if request.POST.get("mode", "") == "send":
        verification.code = code_generator.generate_number_code(settings.ACCOUNTS_APP["code_length"])
    verification.code_signature = signing.Signer().signature(verification.code)
    verification.save()
    return verification

def send_verification_mail(verification, subject, message, error):
    """
        sends verification mail utility. Used in lambda functions for extra readability
    """
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [verification.user.__dict__[UserModel.get_email_field_name()]])
    except Exception as e:
        logger.error(error %e)

def get_verification_link(request):
    """
        Computes the verification link
    """
    verification = create_verification(request)
    if type(verification) is not models.VerificationModel:
        return None
    else:      
        return "%s/%s/verify-link/?u=%s&c=%s" %(request.META["HTTP_HOST"], settings.ACCOUNTS_APP["base_url"], verification.username_signature, verification.code_signature)
    
def get_verification_code(request):
    """
        Computes the verification link
    """
    verification = create_verification(request)
    if type(verification) is not models.VerificationModel:
        return None
    else:      
        return verification.code