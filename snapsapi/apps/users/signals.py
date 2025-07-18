from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from snapsapi.apps.users.models import Profile
from snapsapi.apps.core.models import Collection

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a Profile object for a User instance
    right after it has been created.
    """
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def create_default_collection(sender, instance, created, **kwargs):
    """
    Automatically creates a default Collection for a User instance
    right after it has been created.
    """
    if created:
        Collection.objects.create_collection(
            owner=instance,
            name='default',
            description="Default collection",
            is_public=True
        )
