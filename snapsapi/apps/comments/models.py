import uuid
from django.conf import settings
from django.db import models
from bson.objectid import ObjectId
import shortuuid

from snapsapi.apps.posts.models import Post
from snapsapi.apps.comments import model_managers as mm
from snapsapi.apps.comments import model_mixins as mx


def generate_uuid():
    return uuid.uuid4()


class Comment(models.Model, mx.CommentMixin):
    uid = models.UUIDField(primary_key=True, default=generate_uuid, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes_count = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = mm.CommentManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.content[:20]}"
