import logging
from threading import Thread

logger = logging.getLogger("AccountRecoveryApp.views")

def _send_mail(message, user, subject):
    error = "Failed to send 2FA code to %s" %(user.get_username(), "%s")
    try:
        user.email_user(subject, message)
    except Exception as e:
        logger.error(error %e)

def send_two_factor_token(user, token, duration):
    message = """A login attempt has been made to your account
                Your two factor token is %s valid for %s minutes. 
                If you didn't request the token ignore this message.""" %(token)
    subject = "Two factor authentication token"
    Thread(target=_send_mail, args=(message, user)).start()
    