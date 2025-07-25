import uuid
from django.conf import settings
from django.db import models
from bson.objectid import ObjectId
import shortuuid

from snapsapi.apps.posts.models import Post
from snapsapi.apps.comments.models import Comment
from django.db.models.signals import post_save, post_delete

from django.dispatch import receiver


def generate_short_uuid():
    return shortuuid.uuid()


def generate_oid():
    return str(ObjectId())


class PostLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} likes {self.post}'


class CommentLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} likes {self.comment}'


# --- Signals for automatic likes_count update ---

@receiver(post_save, sender=PostLike)
def increment_post_likes_count(sender, instance, created, **kwargs):
    if created:
        Post.objects.filter(pk=instance.post_id).update(likes_count=models.F('likes_count') + 1)


@receiver(post_delete, sender=PostLike)
def decrement_post_likes_count(sender, instance, **kwargs):
    Post.objects.filter(pk=instance.post_id, likes_count__gt=0).update(likes_count=models.F('likes_count') - 1)


@receiver(post_save, sender=CommentLike)
def increment_comment_likes_count(sender, instance, created, **kwargs):
    if created:
        Comment.objects.filter(pk=instance.comment_id).update(likes_count=models.F('likes_count') + 1)


@receiver(post_delete, sender=CommentLike)
def decrement_comment_likes_count(sender, instance, **kwargs):
    Comment.objects.filter(pk=instance.comment_id, likes_count__gt=0).update(likes_count=models.F('likes_count') - 1)
