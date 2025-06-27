from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from snapsapi.apps.users.models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a Profile object for a User instance
    right after it has been created.
    """
    if created:
        Profile.objects.get_or_create(user=instance)
