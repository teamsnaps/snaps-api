from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from snapsapi.apps.posts.models import Post
from snapsapi.apps.comments.models import Comment
from .models import PostLike, CommentLike
from .serializers import LikeResponseSerializer


class PostLikeToggleView(APIView):
    """
    게시글에 대한 좋아요 토글(생성/삭제)을 처리하는 View입니다.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_uid = self.kwargs.get('uid')
        post = get_object_or_404(Post, uid=post_uid)
        user = request.user

        like, created = PostLike.objects.get_or_create(user=user, post=post)

        if not created:
            like.delete() # 이미 존재하면 삭제 (좋아요 취소)

        post.refresh_from_db()
        serializer = LikeResponseSerializer({
            'likes_count': post.likes_count,
            'is_liked': created
        })
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentLikeToggleView(APIView):
    """
    댓글에 대한 좋아요 토글(생성/삭제)을 처리하는 View입니다.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        uid = self.kwargs.get('uid')
        comment = get_object_or_404(Comment, uid=uid)
        user = request.user

        like, created = CommentLike.objects.get_or_create(user=user, comment=comment)

        if not created:
            like.delete() # 이미 존재하면 삭제 (좋아요 취소)

        comment.refresh_from_db()
        serializer = LikeResponseSerializer({
            'likes_count': comment.likes_count,
            'is_liked': created
        })
        return Response(serializer.data, status=status.HTTP_200_OK)