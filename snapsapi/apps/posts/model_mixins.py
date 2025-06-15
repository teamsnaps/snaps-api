from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from snapsapi.apps.posts.models import Post  # Avoiding Circular References


class PostMixin:
    def update_tags(self: 'Post', tag_names: list[str]) -> None:
        """
        :param tag_names: List of tag name strings
        """
        from snapsapi.apps.posts.models import Tag
        tags = Tag.objects.create_tags(tag_names)
        self.tags.set(tags)

    def attach_images(self: 'Post', urls: list[str]) -> None:
        from snapsapi.apps.posts.models import PostImage
        objs = [
            PostImage(post=self, url=url, order=idx)
            for idx, url in enumerate(urls)
        ]
        PostImage.objects.bulk_create(objs)

    def delete_images(self: 'Post') -> None:
        self.images.all().delete()
