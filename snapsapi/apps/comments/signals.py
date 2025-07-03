from django.dispatch import receiver
from django.db.models.signals import post_save

from snapsapi.apps.comments.models import Comment


@receiver(post_save, sender=Comment)
def update_comment_count(sender, instance, created, update_fields, **kwargs):
    post = instance.post
    # updated_fields = update_fields or []

    if created:
        post.increment_comments_count()
    else:
        post.decrement_comments_count()
    # elif 'is_deleted' in updated_fields:
    #     if instance.is_deleted:
    #         post.decrement_comments_count()
    #     else:
    #         post.increment_comments_count()
