from typing import TYPE_CHECKING
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

    def attach_images(self: 'Post', urls: list[str]) -> None:
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
