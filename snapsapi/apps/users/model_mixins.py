from typing import TYPE_CHECKING

from django.db.models import F

if TYPE_CHECKING:
    from snapsapi.apps.users.models import User


class UserMixin:
    def increment_posts_count(self: 'User'):
        self.posts_count = F('posts_count') + 1
        self.save(update_fields=['posts_count'])
        self.refresh_from_db(fields=['posts_count'])

    def decrement_posts_count(self: 'User'):
        if self.posts_count > 0:
            self.posts_count = F('posts_count') - 1
            self.save(update_fields=['posts_count'])
            self.refresh_from_db(fields=['posts_count'])
