from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'snapsapi.apps.users'

    def ready(self):
        try:
            import snapsapi.apps.users.signals
        except ImportError:
            pass
