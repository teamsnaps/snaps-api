from django.apps import AppConfig


class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'snapsapi.apps.posts'

    def ready(self):
        try:
            import snapsapi.apps.posts.signals
        except ImportError:
            pass