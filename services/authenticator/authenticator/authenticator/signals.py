
from allauth.account.signals import user_logged_out
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(user_logged_out)
def log_out_tokens(request, user, **kwargs):

    # Don't expire tokens if the requst says to hold onto it.
    if request.POST.get('keeptokens'):
        return

    # Expire all existing tokens
    for old_token in Token.objects.filter(user=user):
        old_token.delete()