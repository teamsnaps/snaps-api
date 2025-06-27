from django.db import models
from typing import TYPE_CHECKING

from snapsapi.apps.posts import model_querysets as mq

if TYPE_CHECKING:
    from snapsapi.apps.posts.models import Post, Tag  # Avoiding Circular References


class PostManager(models.Manager):
    def get_queryset(self) -> 'mq.PostQuerySet':
        return mq.PostQuerySet(self.model, using=self._db)

    def create_post(self, user, caption: str, images: list[str], tags: list[str], **extra_fields) -> 'Post':
        """
        Create a Post and associated PostImage instances at once.
        :param user: User instance
        :param caption: str
        :param images: List of image URL strings
        :param tags: List of tag strings
        :param extra_fields: Additional Post fields (e.g., is_deleted, is_active)
        :return: The created Post object
        """
        from snapsapi.apps.posts.models import PostImage
        post = self.create(user=user, caption=caption, **extra_fields)
        for idx, url in enumerate(images):
            PostImage.objects.create(post=post, url=url, order=idx)
        post.update_tags(tags)
        return post

    def get_posts_by_user(self, user):
        return (
            self.get_queryset()
            .filter(user=user)
            .get_posts_with_first_image()
        )  # Todo: Unresolved attribute reference error in Pycharm



class TagManager(models.Manager):
    def create_tags(self, tags) -> list['Tag']:
        tag_objs = []
        for tag_name in tags:
            tag_obj, _ = self.get_or_create(name=tag_name)
            tag_objs.append(tag_obj)
        return tag_objs
