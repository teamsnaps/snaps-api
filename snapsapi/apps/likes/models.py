import uuid
from django.db import models
from django.contrib.auth import get_user_model
from bson.objectid import ObjectId
import shortuuid

from snapsapi.apps.posts.models import Post
from snapsapi.apps.comments.models import Comment


def generate_short_uuid():
    return shortuuid.uuid()


def generate_oid():
    return str(ObjectId())


User = get_user_model()


class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')
