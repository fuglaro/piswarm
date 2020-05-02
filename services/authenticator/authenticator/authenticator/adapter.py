import uuid

from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class AccountAdapter(DefaultAccountAdapter):
    def new_user(self, request):
        user = DefaultAccountAdapter.new_user(self, request)
        # Set the username to be a UUID by default.
        user.username = str(uuid.uuid4())
        return user

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def new_user(self, request, sociallogin):
        user = DefaultSocialAccountAdapter.new_user(self, request, sociallogin)
        # Set the username to be a UUID by default.
        user.username = str(uuid.uuid4())
        return user