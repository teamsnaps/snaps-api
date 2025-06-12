import uuid
from django.db import models
from django.contrib.auth import get_user_model
from bson.objectid import ObjectId
import shortuuid


def generate_short_uuid():
    return shortuuid.uuid()


def generate_oid():
    return str(ObjectId())


User = get_user_model()


# Create your models here.
class Post(models.Model):
    uid = models.CharField(max_length=50, db_index=True, unique=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    images = models.JSONField(default=list, blank=True)
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.caption[:20]}"


class Tag(models.Model):
    uid = models.CharField(default=generate_short_uuid, max_length=22, unique=True, db_index=True, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f": {self.name}"