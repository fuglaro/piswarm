
from allauth.socialaccount.templatetags.socialaccount import *
from allauth.socialaccount.models import SocialApp

# Override to hide unconfigured providers
@register.simple_tag
def get_providers():
    """
    Returns a list of social authentication providers.

    Usage: `{% get_providers as socialaccount_providers %}`.

    Then within the template context, `socialaccount_providers` will hold
    a list of social providers configured for the current site but filtered
    to the ones configured in the admin site.
    """

    apps = providers.registry.get_list()

    configured = set(SocialApp.objects.values_list("provider", flat=True))

    return [app for app in apps if app.id in configured]
