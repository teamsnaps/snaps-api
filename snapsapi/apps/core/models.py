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


class Story(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)





class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')


