import logging
from threading import Thread
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger("AccountRecoveryApp.views")

def _send_mail(message, user, subject):
    error = "Failed to send 2FA code to %s because: %s" %(user.get_username(), "%s")
    try:
        send_mail(
            subject=subject, 
            message=message, 
            recipient_list=[user.email],
            from_email=None
        )
    except Exception as e:
        logger.error(error %e)

def send_two_factor_token(user, token, duration):
    app_name = settings.APP_NAME or ""
    message = """
                A login attempt has been made to your %s account.
                Your two factor token is: %s, valid for %s minutes. 
                If you didn't request the token ignore this 
                message.
            """ %(app_name, token, str(duration))
    subject = "Two factor authentication token"
    Thread(target=_send_mail, args=(message, user, subject)).start()
    