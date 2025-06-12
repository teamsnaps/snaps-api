from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, UpdateAPIView, \
    RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from snapsapi.apps.core.schemas import MOCK_PRIVATE_FEED, MOCK_PUBLIC_FEED
from snapsapi.apps.posts.serializers import WritePostSerializer, ReadPostSerializer, PostSerializer
from snapsapi.apps.posts import models as m
from rest_framework.response import Response
from drf_rw_serializers.generics import ListCreateAPIView

#
# class StoryListCreateView(ListCreateAPIView):
#     queryset = m.Story.objects.all()
#     serializer_class = StorySerializer


class PostListCreateView(ListCreateAPIView):
    queryset = m.Post.objects.filter(is_deleted=False)
    read_serializer_class = ReadPostSerializer
    write_serializer_class = WritePostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # 인증된 유저만 가능

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetailView(UpdateAPIView):
    queryset = m.Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]  # 필요에 따라 커스텀
    lookup_field = 'uid'

    def get_queryset(self):
        return m.Post.objects.filter(user=self.request.user)


# 3. soft delete (flag 변경용)
class PostSoftDeleteView(UpdateAPIView):
    queryset = m.Post.objects.filter(is_deleted=False)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        post.is_deleted = True  # flag 변경
        post.save()
        return Response({'detail': 'soft deleted'}, status=status.HTTP_200_OK)


class FeedMockListView(ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(MOCK_PRIVATE_FEED)
        else:
            return Response(MOCK_PUBLIC_FEED)
