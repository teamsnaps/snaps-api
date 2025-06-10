from django.db import models
from django.contrib.auth.models import AbstractUser
from bson.objectid import ObjectId
import shortuuid


def generate_short_uuid():
    return shortuuid.uuid()


def generate_oid():
    return str(ObjectId())

def generate_username_with_short_uuid():
    suid = generate_short_uuid()[:6]
    return f"User_{suid}"

class User(AbstractUser):
    uid = models.CharField(
        max_length=64, unique=True, editable=False, default=generate_short_uuid,
        db_index=True, help_text="외부 노출용 유저 고유 식별자"
    )
    email = models.EmailField(db_index=True, null=False, blank=False)
    phone_number = models.CharField(max_length=30, null=False, blank=False)
    deleted = models.BooleanField(default=False, null=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    username = models.CharField(max_length=50, unique=True, default=generate_username_with_short_uuid)

    # username = models.CharField(
    #     _("username"),
    #     max_length=150,
    #     unique=True,
    #     help_text=_(
    #         "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    #     ),
    #     validators=[username_validator],
    #     error_messages={
    #         "unique": _("A user with that username already exists."),
    #     },
    # )

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    # image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    image = models.JSONField(default=list, blank=True)
