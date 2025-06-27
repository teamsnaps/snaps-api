from datetime import timedelta, datetime, UTC

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator

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
    is_deleted = models.BooleanField(default=False, null=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    username = models.CharField(
        max_length=30,  # Set max length to 30 characters
        unique=True,
        default=generate_username_with_short_uuid,
        validators=[MinLengthValidator(5)]  # Add a validator for minimum length of 5
    )
    is_username_changed = models.BooleanField(
        default=False,
        help_text="Becomes True if the user has changed their initial username at least once."
    )
    username_last_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Stores the timestamp of the last username change."
    )

    followers_count = models.PositiveIntegerField(default=0, db_index=True)
    following_count = models.PositiveIntegerField(default=0, db_index=True)

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

    def can_change_username(self):
        """
        Checks if the user is allowed to change their username.
        Returns True if 30 days have passed since the last change, or if it has never been changed.
        """
        if not self.is_username_changed:
            return True
        if self.username_last_changed_at:
            # Check if 30 days have passed
            return datetime.now(UTC) > self.username_last_changed_at + timedelta(days=30)
        # This case should ideally not be reached if is_username_changed is True, but acts as a fallback.
        return True


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=50, blank=True)
    # image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    image_url = models.CharField(max_length=255, default='')
