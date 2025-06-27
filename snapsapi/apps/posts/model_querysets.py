from django.db import models
from django.db.models import Subquery, OuterRef




class PostQuerySet(models.QuerySet):
    def get_first_image_urls(self):
        """
        Returns a list of the first image URL for each post in the queryset.
        This is highly efficient as it uses a single database query.
        """
        from snapsapi.apps.posts.models import PostImage

        # 1. Create a subquery that gets the URL of the first image for a given post (OuterRef('pk'))
        first_image_sq = PostImage.objects.filter(
            post=OuterRef('pk')
        ).order_by('id').values('url')[:1]  # Use 'id' or 'created_at' for ordering

        # 2. Annotate the main queryset with the result of the subquery
        # 3. Use values_list to select only our new annotated field
        return self.annotate(
            first_image_url=Subquery(first_image_sq)
        ).values_list('first_image_url', flat=True)
