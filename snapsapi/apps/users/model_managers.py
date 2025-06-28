from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from snapsapi.apps.users.exceptions import UserNotExistException
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from snapsapi.apps.users.models import User  # Avoiding Circular References


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        username = extra_fields.pop('username', None)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

    def get_user_by_uid(self, uid: str):
        """
        Find and return a user by their public UID.
        Returns None if the user does not exist.
        """
        try:
            # Use self.get() which is available on any manager.
            return self.get(uid=uid)
        except ObjectDoesNotExist:
            raise UserNotExistException()

    def get_followers(self, user: 'User'):
        follower_relations = user.followers_count
