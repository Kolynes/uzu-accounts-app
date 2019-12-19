from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect
from django.conf import settings

def ensure_signed_in(func):
    """A decorator to ensure that a session is active before attempting any sensitive operation."""
    def decorated_func(request):
        if request.user.is_authenticated:
            return func(request)
        if request.is_ajax():
            return JsonResponse({
                "status": False,
                "error": "Not signed in"
            })
        return redirect(settings.LOGIN_URL + '?next=' + request.path)
    return decorated_func

def ensure_super_user(func):
    """A decorator to ensure that a superuser is active is active before attempting any sensitive operations."""
    def decorated_func(request):
        if request.user.is_superuser and request.user.is_authenticated:
            return func(request)
        if request.is_ajax():
            return JsonResponse({
                "status": False,
                "error": "This is not a superuser account"
            })
        return redirect(settings.LOGIN_URL)
    return decorated_func

def ensure_staff(func):
    """A decorator to ensure that a staff or a uper user is active before attempting privileged operations."""
    def decorated_func(request):
        if request.user.is_staff and request.user.is_authenticated:
            return func(request)
        if request.user.is_superuser and request.user.is_authenticated:
            return func(request)
        if request.is_ajax():
            return JsonResponse({
                "status": False,
                "error": "This is not a staff account"
            })
        return redirect(settings.LOGIN_URL)
    return decorated_func

