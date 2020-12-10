from AccountsApp.views import verify_2fa
from django.urls import path
from . import views

urlpatterns = [
    path("send-verification-code/", views.send_verification_code),
    path("send-verification-link/", views.send_verification_link),
    path("verify-code/", views.verify_code),
    path("verify-link/", views.verify_link),
    path("verify-2fa/", views.verify_2fa),
    path("reset-password/", views.reset_password),
    path("change-password/", views.change_password),
    path("sign-in/", views.sign_in),
    path("sign-up/", views.sign_up),
    path("sign-out/", views.sign_out),
    path("authenticate/", views.authenticate_user)
]
