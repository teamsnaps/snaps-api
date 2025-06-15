from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, UpdateAPIView, \
    RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from snapsapi.apps.posts.schemas import MOCK_PRIVATE_FEED, MOCK_PUBLIC_FEED
from snapsapi.apps.posts.serializers import PostCreateSerializer, PostUpdateSerializer
from snapsapi.apps.posts import models as m
from rest_framework.response import Response
from drf_rw_serializers.generics import ListCreateAPIView

#
# class StoryListCreateView(ListCreateAPIView):
#     queryset = m.Story.objects.all()
#     serializer_class = StorySerializer


class PostListCreateView(ListCreateAPIView):
    queryset = m.Post.objects.filter(is_deleted=False)
    read_serializer_class = PostCreateSerializer
    write_serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # 인증된 유저만 가능

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetailView(UpdateAPIView):
    queryset = m.Post.objects.all()
    serializer_class = PostUpdateSerializer
    permission_classes = [IsAuthenticated]  # 필요에 따라 커스텀
    lookup_field = 'uid'

    def get_queryset(self):
        return m.Post.objects.filter(user=self.request.user)





class FeedMockListView(ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(MOCK_PRIVATE_FEED)
        else:
            return Response(MOCK_PUBLIC_FEED)
