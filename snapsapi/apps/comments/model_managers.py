from django.db import models


class CommentManager(models.Manager):
    def create_comment(self, user, post, content, parent=None):
        comment = self.create(
            user=user,
            post=post,
            content=content,
            parent=parent
        )
        return comment
