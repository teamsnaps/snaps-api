from typing import TYPE_CHECKING
from datetime import datetime, UTC

if TYPE_CHECKING:
    from snapsapi.apps.comments.models import Comment  # Avoiding Circular References



class CommentMixin:
    def soft_delete(self: 'Comment') -> None:
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
