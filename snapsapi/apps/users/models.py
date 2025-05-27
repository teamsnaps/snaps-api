from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(db_index=True, null=False, blank=False)
    phone_number = models.CharField(max_length=30, null=False, blank=False)
    deleted = models.BooleanField(default=False, null=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    # image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    image = models.JSONField(default=list, blank=True)