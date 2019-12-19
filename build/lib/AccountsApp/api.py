def get_verification_link(request):
    """
        Computes the verification link
    """
    verification = create_verification(request)
    if type(verification) is not models.Verification:
        return None
    else:      
        return "%s/%s/verify-link/?u=%s&c=%s" %(request.META["HTTP_HOST"], settings.ACCOUNTS_APP["base_url"], verification.username_signature, verification.code_signature)
    
def get_verification_code(request):
    """
        Computes the verification link
    """
    verification = create_verification(request)
    if type(verification) is not models.Verification:
        return None
    else:      
        return verification.code

