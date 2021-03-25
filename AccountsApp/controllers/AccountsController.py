from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from AccountsApp import models
from utils import code_generator
from utils.shortcuts import json_response, dictify
from utils.decorators import ensure_signed_in, ensure_post
from utils.controller import Controller
from AccountsApp import services
import logging
from threading import Thread
from django.conf import settings
from django.core import signing
import re
from django.db import IntegrityError
from django.core.mail import send_mail
from AccountsApp import signals 

logger = logging.getLogger("AccountRecoveryApp.views")
UserModel = get_user_model()

class AccountsController(Controller):

    @Controller.route()
    @Controller.decorate(ensure_post)
    def sign_in(self, request):
        user = authenticate(request, **dictify(request.POST))
        if user:
            if request.GET.get("r", "false") == "false":
                request.session.set_expiry(0)
            login(request, user)
            signals.signed_in.send(sender="sign_in", request=request, user=user)
            return json_response(200)
        return json_response(401, error={
            "summary": "Invalid username or password"
        })

    @Controller.route()
    @Controller.decorate(ensure_post)
    def sign_up(self, request):
        try:
            user = UserModel(**dictify(request.POST))
            user.set_password(request.POST["password"])
            user.save()
            if request.GET.get("r", "false") == "false":
                request.session.set_expiry(0)
            login(request, user)
            signals.signed_up.send(sender="sign_up", request=request, user=user)
            return json_response(201)
        except IntegrityError as e:
            print(e)
            return json_response(401, error={
                "summary": "Failed to create account",
                "fields": e.args
            })

    @Controller.route()
    @Controller.decorate(ensure_post)
    def authenticate_user(self, request):
        if request.user.check_password(request.POST["password"]):
            return json_response(200)
        else:
            return json_response(401)

    @Controller.route()
    def sign_out(self, request):
        try:
            logout(request)
        except:
            pass
        signals.signed_out.send(sender="sign_out")
        return json_response(200)

    @Controller.route()
    @Controller.decorate(ensure_post, ensure_signed_in)
    def change_password(self, request):
        if authenticate(username=request.user._wrapped.__dict__[request.user.USERNAME_FIELD], password=request.POST["old_password"]):
            request.user.set_password(request.POST["new_password"])
            signals.password_changed.send(sender="change_password", request=request, user=request.user)
            return json_response(200)
        return json_response(401, error={
            "summary": "incorrect password"
        })

    @Controller.route()
    @Controller.decorate(ensure_post)
    def reset_password(self, request):
        try:
            verification = models.VerificationModel.objects.get(**{
                "user__%s" %UserModel.USERNAME_FIELD: request.POST["username"],
                "code": request.POST["code"]
            })
            if not verification.recovery:
                return json_response(404, error={
                    "summary": "Incorrect verification code."
                })
            verification.recovery = False
            verification.user.set_password(request.POST["new_password"])
            verification.user.save()
            signals.password_reset.send(sender="reset_password", request=request, verification=verification)
        except models.VerificationModel.DoesNotExist:
            return json_response(404, error={
                "summary": "Incorrect verification code."
            })
        return json_response(200)

    @Controller.route()
    def verify_link(self, request):
        try:
            verification = models.VerificationModel.objects.get(username_signature=request.GET["u"], code_signature=request.GET["c"])
            if not verification.recovery:
                return HttpResponseNotFound()
            verification.verified = True
            verification.save()
            if settings.ACCOUNTS_APP["sign_in_after_verification"]:
                login(request, verification.user)
            signals.link_verified.send(sender="verify_link", request=request, verification=verification)
            return HttpResponseRedirect("{0}?u={1}&c={2}".format(settings.ACCOUNTS_APP["redirect_link"], request.GET["u"], request.GET["c"]))
        except models.VerificationModel.DoesNotExist:
            return HttpResponseNotFound()

    @Controller.route()
    @Controller.decorate(ensure_post)
    def verify_code(self, request):
        try:
            verification = models.VerificationModel.objects.get(**{
                "user__%s" %UserModel.USERNAME_FIELD: request.POST["username"],
                "code": request.POST["code"]
            })
            if not verification.recovery:
                return json_response(404, error={
                    "summary": "Incorrect verification code."
                })
            verification.verified = True
            verification.save()
            signals.code_verified.send(sender="verify_code", request=request, verification=verification)
            return json_response(200)
        except models.VerificationModel.DoesNotExist:
            return json_response(404, error={
                "summary": "Incorrect verification code."
            })
    
    @Controller.route()
    def send_verification_code(self, request):
        verification = services.create_verification(request)
        if type(verification) is not models.VerificationModel:
            return verification
        message = "Your verification code is %s" %(verification.code)
        verification.recovery = True
        verification.save()
        error = "Failed to send verification code to %s <%s> by email\n %s" %(verification.user.__dict__[UserModel.USERNAME_FIELD], verification.user.__dict__[UserModel.get_email_field_name()], "%s")
        Thread(target=lambda: services.send_verification_mail(verification, "Account VerificationModel", message, error)).start()
        signals.verification_code_sent.send(sender="send_verification_code", request=request, verification=verification)
        return json_response(200)
