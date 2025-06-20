import uuid
from django.db import models

from snapsapi.apps.users.models import User
from snapsapi.apps.posts import model_managers as mm
from snapsapi.apps.posts import model_mixins as mx


# from bson.objectid import ObjectId
# import shortuuid

def generate_uuid():
    return uuid.uuid4()


class Tag(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = mm.TagManager()

    def __str__(self):
        return self.name


class PostImage(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='images')
    url = models.URLField()
    order = models.PositiveIntegerField(default=0)  # 이미지 순서
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.post} - {self.order}"


class Post(models.Model, mx.PostMixin):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = mm.PostManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.caption[:20]}"
