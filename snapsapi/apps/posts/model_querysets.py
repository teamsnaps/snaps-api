from django.db import models
from django.db.models import Subquery, OuterRef, Window
from django.db.models.aggregates import Count


class PostQuerySet(models.QuerySet):
    def get_posts_with_first_image(self):
        """
        For each post in the QuerySet, returns a list of dictionaries containing
        key fields of the Post and the URL of its first image.
        This is highly efficient as it uses a single database query.
        """
        from snapsapi.apps.posts.models import PostImage

        # 1. Create a subquery to get the URL of the first image for each post.
        first_image_sq = PostImage.objects.filter(
            post=OuterRef('pk')
        ).order_by('order').values('url')[:1]  # Select only the url of the first object after ordering.

        # 2. Annotate the main queryset with the subquery result.
        qs = self.annotate(
            first_image_url=Subquery(first_image_sq)
            # total_posts=Window(expression=Count('pk'))
        )

        # 3. Select the required Post fields and the newly annotated field.
        return qs.values(
            'uid',
            # 'caption',
            # 'likes_count',
            # 'comments_count',
            # 'created_at',
            'first_image_url',  # The field added via annotate.
        )

    def get_posts_by_user(self, user):
        return self.filter(user=user)
