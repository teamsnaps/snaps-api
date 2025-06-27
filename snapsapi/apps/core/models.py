import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from bson.objectid import ObjectId
import shortuuid
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from snapsapi.apps.core import model_managers as mm


def generate_short_uuid():
    return shortuuid.uuid()


def generate_oid():
    return str(ObjectId())


User = get_user_model()


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = mm.FollowManager()

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'


# --- Signals for automatic count update ---

@receiver(post_save, sender=Follow)
def increment_follow_counts(sender, instance, created, **kwargs):
    """
    Follow 객체가 생성될 때(created=True),
    팔로우를 한 유저(follower)의 following_count와
    팔로우를 받은 유저(following)의 followers_count를 1씩 증가시킵니다.
    """
    if created:
        follower = instance.follower
        following = instance.following

        # F() expression을 사용하여 race condition을 방지합니다.
        follower.following_count = models.F('following_count') + 1
        follower.save(update_fields=['following_count'])

        following.followers_count = models.F('followers_count') + 1
        following.save(update_fields=['followers_count'])


@receiver(post_delete, sender=Follow)
def decrement_follow_counts(sender, instance, **kwargs):
    """
    Follow 객체가 삭제될 때,
    관련된 유저들의 카운트를 1씩 감소시킵니다.
    """
    follower = instance.follower
    following = instance.following

    # 0보다 클 때만 감소시키도록 조건을 추가하여 안정성을 높입니다.
    follower.following_count = models.F('following_count') - 1
    follower.save(update_fields=['following_count'])

    following.followers_count = models.F('followers_count') - 1
    following.save(update_fields=['followers_count'])
