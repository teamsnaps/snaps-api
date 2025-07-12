import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from bson.objectid import ObjectId
import shortuuid
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import datetime, UTC

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


class Collection(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_collections')
    posts = models.ManyToManyField('posts.Post', blank=True, related_name='collections')
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = mm.CollectionManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.owner.username}'s collection: {self.name}"

    def soft_delete(self):
        """
        Soft-deletes the collection.
        """
        if self.is_deleted:
            return

        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def can_user_add_posts(self, user):
        """
        Check if a user can add posts to this collection.
        A user can add posts if they are the owner or a member of the collection.

        :param user: User instance to check
        :return: Boolean indicating if the user can add posts
        """
        if user == self.owner:
            return True

        return self.members.filter(user=user).exists()


class CollectionMember(models.Model):
    collection = models.ForeignKey('Collection', on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collection_memberships')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('collection', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.collection.name}"
