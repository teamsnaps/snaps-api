from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from snapsapi.apps.posts.models import Post

User = get_user_model()


@receiver(post_save, sender=Post)
def update_user_posts_count_on_save_or_soft_delete(sender, instance, created, update_fields, **kwargs):
    """
    게시물이 생성, soft-delete 또는 복원될 때 User의 posts_count를 업데이트합니다.
    - 생성: 카운트 +1
    - Soft-delete (is_deleted: False -> True): 카운트 -1
    - 복원 (is_deleted: True -> False): 카운트 +1
    """
    user = instance.user
    updated_fields = update_fields or []

    if created:
        user.increment_posts_count()
    elif 'is_deleted' in updated_fields:
        if instance.is_deleted:
            user.decrement_posts_count()
        else:
            user.increment_posts_count()
