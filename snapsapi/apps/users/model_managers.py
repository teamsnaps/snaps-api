from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from snapsapi.apps.users.exceptions import UserNotExistException
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from snapsapi.apps.users.models import User  # Avoiding Circular References


class UserManager(BaseUserManager):
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
