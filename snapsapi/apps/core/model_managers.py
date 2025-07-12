from typing import TYPE_CHECKING

from django.db import models

from snapsapi.apps.core.exceptions import FollowYourselfException

if TYPE_CHECKING:
    from snapsapi.apps.users.models import User
    from snapsapi.apps.core.models import Follow, Collection


class FollowManager(models.Manager):
    def follow(self, follower: 'User', following: 'User') -> tuple['Follow', bool]:
        """
        Creates a follow relationship where 'follower' follows 'following'.
        If the relationship already exists, it returns the existing object without making any changes.

        :param follower: The user requesting to follow
        :param following: The user being followed
        :return: A tuple of (Follow object, boolean indicating if created)
        """
        if follower == following:
            raise FollowYourselfException()

        # Using get_or_create retrieves the existing object if it exists,
        # or creates a new one if it doesn't, preventing duplicate creation.
        obj, created = self.get_or_create(follower=follower, following=following)
        return obj, created

    def unfollow(self, follower: 'User', following: 'User') -> int:
        """
        Deletes the follow relationship where 'follower' follows 'following'.

        :param follower: The user requesting to unfollow
        :param following: The user being unfollowed
        :return: Number of deleted objects (0 or 1)
        """
        # filter().delete() returns 0 without raising an error if the target doesn't exist.
        deleted_count, _ = self.filter(follower=follower, following=following).delete()
        return deleted_count


class CollectionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=True)

    def create_collection(self, owner, name, description="", is_public=True, **extra_fields) -> 'Collection':
        """
        Create a Collection.
        :param owner: User instance who owns the collection
        :param name: Collection name
        :param description: Collection description
        :param is_public: Whether the collection is public
        :param extra_fields: Additional Collection fields
        :return: The created Collection object
        """
        collection = self.create(
            owner=owner,
            name=name,
            description=description,
            is_public=is_public,
            **extra_fields
        )
        return collection

    def get_collections_by_user(self, user):
        """
        Get all collections owned by a user.
        :param user: User instance
        :return: QuerySet of collections
        """
        return self.filter(owner=user)

    def get_collections_with_membership(self, user):
        """
        Get all collections where the user is a member (but not the owner).
        :param user: User instance
        :return: QuerySet of collections
        """
        return self.filter(members__user=user).exclude(owner=user)
