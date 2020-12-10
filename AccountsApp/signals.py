from django.contrib.auth import get_user_model
from django.dispatch import Signal
from django.http import request

SignedUp = Signal(providing_args=["user", "request"])
