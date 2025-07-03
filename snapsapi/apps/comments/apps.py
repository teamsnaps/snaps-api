from django.apps import AppConfig


class CommentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'snapsapi.apps.comments'

    def ready(self):
        try:
            import snapsapi.apps.comments.signals
        except ImportError:
            pass