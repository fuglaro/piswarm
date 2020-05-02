from django.apps import AppConfig

class AppConfig(AppConfig):
    name = 'authenticator'

    def ready(self):
        from . import signals