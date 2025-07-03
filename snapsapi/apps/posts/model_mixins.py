from django.db.models import F
from typing import TYPE_CHECKING, Any
from datetime import datetime, UTC

if TYPE_CHECKING:
    from snapsapi.apps.posts.models import Post  # Avoiding Circular References


class PostMixin:
    def update_tags(self: 'Post', tag_names: list[str]) -> None:
        """
        Updates the tags for the post.
        :param tag_names: A list of tag name strings.
        """
        from snapsapi.apps.posts.models import Tag
        tags = Tag.objects.create_tags(tag_names)
        self.tags.set(tags)

    # def attach_images(self: 'Post', urls: list[dict[str, Any]] | list[Any]) -> None:
    def attach_images(self: 'Post', urls) -> None:
        """
        Attaches a list of images to the post.
        :param urls: A list of image URLs to attach.
        """
        from snapsapi.apps.posts.models import PostImage
        objs = [
            PostImage(post=self, url=url, order=idx)
            for idx, url in enumerate(urls)
        ]
        PostImage.objects.bulk_create(objs)

    def delete_images(self: 'Post') -> None:
        """
        Deletes all images associated with the post.
        """
        self.images.all().delete()

    def soft_delete(self: 'Post') -> None:
        """
        Soft-deletes the post.

        This method sets the is_deleted flag to True, records the deletion
        timestamp, and saves the changes to the database.
        """
        if self.is_deleted:
            # Todo: error must raised, already deleted.
            return

        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def increment_comments_count(self: 'Post'):
        # self.comments_count = self.comments_count + 1
        self.comments_count = F('comments_count') + 1
        self.save(update_fields=['comments_count'])
        self.refresh_from_db(fields=['comments_count'])

    def decrement_comments_count(self: 'Post'):
        if self.comments_count > 0:
            self.comments_count = F('comments_count') - 1
            self.save(update_fields=['comments_count'])
            self.refresh_from_db(fields=['comments_count'])
