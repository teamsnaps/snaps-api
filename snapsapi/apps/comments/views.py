from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from snapsapi.apps.notifications.services import FCMService
from snapsapi.apps.comments.permissions import IsCommentOwner
from snapsapi.apps.comments.models import Comment
from snapsapi.apps.comments.serializers import (
    CommentReadSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
    CommentDeleteSerializer,
)

from snapsapi.apps.posts.models import Post



class CommentListCreateView(ListCreateAPIView):
    """
    GET: Retrieves the list of comments for a specific post.
    POST: Creates a new comment on a specific post.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Receives the Post's uid from URL parameter (self.kwargs['uid']),
        and filters only the top-level comments attached to that Post.
        """
        post_uid = self.kwargs['uid']
        # Optimizes DB query performance using select_related and prefetch_related
        return Comment.objects.filter(is_deleted=False, post__uid=post_uid, parent__isnull=True) \
            .select_related('user', 'user__profile') \
            .prefetch_related('replies')

    def get_serializer_class(self):
        """
        Returns different Serializers based on the request method.
        - GET request: CommentReadSerializer (read-only)
        - POST request: CommentCreateSerializer (write-only)
        """
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentReadSerializer

    def get_serializer_context(self):
        """
        Adds the Post object to the Serializer's context.
        This allows the Serializer to use the Post information received from the URL.
        """
        context = super().get_serializer_context()
        post_uid = self.kwargs['uid']
        context['post'] = get_object_or_404(Post, uid=post_uid)
        return context

    def create(self, request, *args, **kwargs):
        """
        Checks if the post has been deleted before creating a new comment.
        """
        # Get the Post object through the Serializer context
        context = self.get_serializer_context()
        post = context.get('post')

        # Check the is_deleted flag of the post
        if post.is_deleted:
            # If the post is deleted, return a 403 Forbidden error
            return Response(
                {"detail": "Cannot write comments on a deleted post."},
                status=status.HTTP_403_FORBIDDEN
            )

        # If the post is not deleted, perform the default create action
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def send_notification(self, instance):
        # 알림 발송 등의 추가 작업
        # 예: FCM 알림 발송
        try:
            post_owner = instance.post.user
            # 댓글 작성자가 게시물 주인이 아닌 경우에만 알림 발송
            if self.request.user != post_owner:
                fcm_service = FCMService()
                fcm_service.send_notifications_to_user(
                    user_id=post_owner.id,
                    title="새 댓글 알림",
                    body=f"{self.request.user.username}님이 회원님의 게시물에 댓글을 남겼습니다.",
                    data={
                        # "url": f"/posts/{instance.post.uid}?comment={instance.uid}",
                        # "url": "/",
                        "type": "new_comment",
                        "post_id": str(instance.post.uid),
                        "comment_id": str(instance.uid)
                    }
                )
        except Exception as e:
            # 알림 발송 실패가 API 응답에 영향을 주지 않도록 예외 처리
            print(f"알림 발송 실패: {e}")

    def perform_create(self, serializer):
        # 객체 생성
        instance = serializer.save()

        # 객체 생성 후 추가 작업 수행
        self.send_notification(instance)

        return instance





class CommentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated, IsCommentOwner]
    lookup_field = 'uid'

    http_method_names = ['patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method.
        - PATCH: Uses CommentUpdateSerializer for validation.
        - DELETE: Uses an empty CommentDeleteSerializer.
        """
        if self.request.method in ['PATCH']:
            return CommentUpdateSerializer
        return CommentDeleteSerializer

    def destroy(self, request, *args, **kwargs):
        """ Overrides the default destroy action to perform a soft delete. """
        self.get_object().soft_delete()
        return Response({'detail': 'soft deleted'}, status=status.HTTP_204_NO_CONTENT)
