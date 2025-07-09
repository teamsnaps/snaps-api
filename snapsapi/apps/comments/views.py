from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

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
    GET: 특정 게시물의 댓글 목록을 조회합니다.
    POST: 특정 게시물에 새 댓글을 생성합니다.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        URL 파라미터(self.kwargs['uid'])로 Post의 uid를 받아,
        해당 Post에 달린 최상위 댓글들만 필터링합니다.
        """
        post_uid = self.kwargs['uid']
        # select_related와 prefetch_related로 DB 쿼리 성능을 최적화합니다.
        return Comment.objects.filter(is_deleted=False, post__uid=post_uid, parent__isnull=True) \
            .select_related('user', 'user__profile') \
            .prefetch_related('replies')

    def get_serializer_class(self):
        """
        요청 메서드에 따라 다른 Serializer를 반환합니다.
        - GET 요청 시: CommentReadSerializer (읽기 전용)
        - POST 요청 시: CommentCreateSerializer (쓰기 전용)
        """
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentReadSerializer

    def get_serializer_context(self):
        """
        Serializer의 context에 Post 객체를 추가하여 전달합니다.
        이를 통해 Serializer 내부에서 URL로 받은 Post 정보를 사용할 수 있습니다.
        """
        context = super().get_serializer_context()
        post_uid = self.kwargs['uid']
        context['post'] = get_object_or_404(Post, uid=post_uid)
        return context

    def create(self, request, *args, **kwargs):
        """
        새 댓글을 생성하기 전에 게시물이 삭제되었는지 확인합니다.
        """
        # Serializer 컨텍스트를 통해 Post 객체를 가져옵니다.
        context = self.get_serializer_context()
        post = context.get('post')

        # 게시물의 is_deleted 플래그를 확인합니다.
        if post.is_deleted:
            # 삭제된 게시물인 경우, 403 Forbidden 에러를 반환합니다.
            return Response(
                {"detail": "삭제된 게시물에는 댓글을 작성할 수 없습니다."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 게시물이 삭제되지 않았다면, 기본 create 동작을 수행합니다.
        return super().create(request, *args, **kwargs)


class CommentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated, IsCommentOwner]
    lookup_field = 'uid'

    http_method_names = ['patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method.
        - PUT/PATCH: Uses PostUpdateSerializer for validation.
        - DELETE: Uses an empty PostDeleteSerializer.
        """
        if self.request.method in ['PATCH']:
            return CommentUpdateSerializer
        return CommentDeleteSerializer

    def destroy(self, request, *args, **kwargs):
        """ Overrides the default destroy action to perform a soft delete. """
        self.get_object().soft_delete()
        return Response({'detail': 'soft deleted'}, status=status.HTTP_204_NO_CONTENT)
