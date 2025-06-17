from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, UpdateAPIView, \
    RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from snapsapi.apps.posts.serializers import PostCreateSerializer, PostUpdateSerializer
from snapsapi.apps.posts import models as m
from rest_framework.response import Response
from drf_rw_serializers.generics import ListCreateAPIView
from rest_framework.decorators import api_view


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


@api_view(['GET'])
def home(request):
    """
    루트 경로에서 단순 텍스트 메시지를 JSON 형태로 반환
    """
    return Response({
        "message": "Snaps API is running!"
    })


@api_view(['GET'])
def health_check(request):
    """
    /core/health/ 헬스체크 엔드포인트
    status: ok JSON 반환
    """
    return Response({
        "status": "ok"
    })
