from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from . import models
from .utils import code_generator
from .utils.shortcuts import json_response
from .utils.decorators import ensure_signed_in
from .api import get_verification_code, get_verification_link
import logging
from threading import Thread
from django.conf import settings
from django.core import signing
import re

logger = logging.getLogger("AccountRecoveryApp.views")
User = get_user_model()

def create_verification(request):
    """
        creates a verification object and attaches it to the user
    """
    username = request.POST.get("username")
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return json_response(False, error="Account not found")
    else:
        user = request.user
    verification, created = models.Verification.objects.get_or_create(user=user)
    if created or not verification.username_signature:
        verification.username_signature = signing.Signer().signature(user.username)
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
        verification.user.email_user(subject, message)
    except Exception as e:
        logger.error(error %e)

def send_verification_code(request):
    """
        Sends a verification code to the user via email. 
        This view is used for both sending and resending the code depending on the value of the GET variable "mode".
    """
    verification = create_verification(request)
    if type(verification) is not models.Verification:
        return verification
    message = "Hello %s,\n\tYour verification code is %s" %(verification.user.first_name, verification.code)
    verification.recovery = True
    verification.save()
    error = "Failed to send verification code to %s <%s> by email\n %s" %(verification.user.username, verification.user.email, "%s")
    Thread(target=lambda: send_verification_mail(verification, "Account Verification", message, error)).start()
    return json_response(True)

def send_verification_link(request):
    """
        sends the user a link for verification
    """
    verification = create_verification(request)
    if type(verification) is not models.Verification:
        return verification
    message = "Hello %s,\n\tPlease follow the link below to verify your account\n %s/%s/verify-link/?u=%s&c=%s" %(verification.user.first_name, request.META["HTTP_HOST"], settings.ACCOUNTS_APP["base_url"], verification.username_signature, verification.code_signature)
    verification.recovery = True
    verification.save()
    error = "Failed to send verification code to %s <%s> by email\n %s" %(verification.user.username, verification.user.email, "%s")
    Thread(target=lambda: send_verification_mail(verification, "Account Verification", message, error)).start()
    return json_response(True)

def verify_code(request):
    """ 
        Verifies the user via code.
    """
    try:
        verification = models.Verification.objects.get(user__username=request.POST["username"], code=request.POST["code"])
        if not verification.recovery:
            return json_response(False, error="Incorrect verification code.")
        verification.verified = True
        verification.save()
        return json_response(True)
    except models.Verification.DoesNotExist:
        return json_response(False, error="Incorrect verification code.")

def verify_link(request):
    """ 
        Verifies the user via link.
    """
    try:
        verification = models.Verification.objects.get(username_signature=request.GET["u"], code_signature=request.GET["c"])
        if not verification.recovery:
            return json_response(False, error="Incorrect verification code.")
        verification.verified = True
        verification.save()
        if settings.ACCOUNTS_APP["sign_in_after_verification"]:
            login(request, verification.user)
        return HttpResponseRedirect("{0}?u={1}&c={2}".format(settings.ACCOUNTS_APP["redirect_link"], request.GET["u"], request.GET["c"]))
    except models.Verification.DoesNotExist:
        return HttpResponseNotFound()

def reset_password(request):
    """
        Resets the password of the user.
    """
    try:
        verification = models.Verification.objects.get(user__username=request.POST["username"], code=request.POST["code"])
        if not verification.recovery:
            return HttpResponseNotFound()
        verification.recovery = False
        verification.user.set_password(request.POST["newPassword"])
        verification.user.save()
    except models.Verification.DoesNotExist:
        return json_response(False, error="Incorrect verification code.")
    return json_response(True)

@ensure_signed_in
def change_password(request):
    """
        changes the password of the user
    """
    if authenticate(username=request.user.username, password=request.POST["oldPassword"]):
        request.user.set_password(request.POST["newPassword"])
        login(request, request.user)
        return json_response(True)
    return json_response(False, error="Invalid password")

def sign_in(request):
    """
        logs the user in
    """
    if len(re.findall("^[a-zA-Z0-9]{3,}@[a-zA-Z0-9]{3,}\.[a-zA-Z0-9]{2,}$", request.POST["username"])) == 1:
        if User.objects.filter(email=request.POST["username"]).exists():
            username = User.objects.get(email=request.POST["username"]).username
        else:
            return json_response(False, error="Incorrect username/email or password")
    else:
        username = request.POST["username"].title().strip()
    user = authenticate(username=username, password=request.POST["password"])
    if user:
        if request.POST.get("keepSignedIn", "false") == "false":
            request.session.set_expiry(0)
        login(request, user)
        return json_response(True)
    return json_response(False, error="Incorrect username/email or password")

def sign_up(request):
    """
        creates a new user
    """
    if User.objects.filter(email=request.POST["email"]).exists():
        return json_response(False, error="This email is not available")
    try:
        user = User(
            first_name=request.POST["firstName"].title().strip(),                                                                                                                                                                                       last_name=request.POST["lastName"].title().strip(),
            email=request.POST["email"].lower().strip(),
            username=request.POST["username"].title().strip(),
        )
        user.set_password(request.POST["password"])
        user.save()
        if request.POST["keepSignedIn"] == "false":
            request.session.set_expiry(0)
        login(request, user)
        return json_response(True)
    except IntegrityError as e:
        print(e)
        return json_response(False, error="This username is not available")

@ensure_signed_in
def authenticate_user(request):
    """
        authenticates the usser
    """
    if authenticate(username=request.user.username, password=request.POST["password"]):
        return json_response(True)
    else:
        return json_response(False)

def sign_out(request):
    """
        signs out the user
    """
    try:
        logout(request)
    except:
        pass
    return json_response(True)
