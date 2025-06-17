from django.utils.decorators import method_decorator
from rest_framework.generics import UpdateAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import boto3
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from snapsapi.apps.posts.serializers import PostCreateSerializer, PresignedURLRequestSerializer, PostUpdateSerializer, \
    PostDeleteSerializer, PostReadSerializer
from snapsapi.apps.posts.schemas import (
    POST_CREATE_REQUEST_EXAMPLE,
    POST_CREATE_RESPONSE_EXAMPLE,
    PRESIGNED_POST_URL_RESPONSE_EXAMPLE,
    PRESIGNED_POST_URL_REQUEST_EXAMPLE,
)

from snapsapi.apps.posts.utils import create_presigned_post, build_object_name
from drf_rw_serializers.generics import GenericAPIView, UpdateAPIView
from snapsapi.apps.posts.models import Post
from django.db import transaction
from snapsapi.apps.posts.schemas import MOCK_PRIVATE_FEED, MOCK_PUBLIC_FEED

@method_decorator(transaction.atomic, name='dispatch')
class PostCreateView(GenericAPIView):
    # """
    # Handles the creation of a new post.
    # The entire process is wrapped in a database transaction. If any part of the
    # post creation fails (e.g., attaching images or tags), the entire transaction
    # will be rolled back, ensuring data consistency.
    # """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="게시글 작성",
        description="여러 이미지와 태그를 포함한 게시글을 생성합니다.",
        request=PostCreateSerializer,
        examples=POST_CREATE_REQUEST_EXAMPLE,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=PostCreateSerializer,
                description="게시글 등록 성공",
                examples=POST_CREATE_RESPONSE_EXAMPLE,
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="잘못된 요청"
            ),
        },
        auth=None,
        tags=["Posts"],
    )
    def post(self, request):
        serializer = PostCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            post = serializer.save()
            return Response(serializer.to_representation(post),
                            status=status.HTTP_201_CREATED)  # Todo: attach read serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(transaction.atomic, name='dispatch')
class PostListCreateView(ListCreateAPIView):
    # """
    # Handles the creation of a new post.
    # The entire process is wrapped in a database transaction. If any part of the
    # post creation fails (e.g., attaching images or tags), the entire transaction
    # will be rolled back, ensuring data consistency.
    # """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="게시글 작성",
        description="여러 이미지와 태그를 포함한 게시글을 생성합니다.",
        request=PostCreateSerializer,
        examples=POST_CREATE_REQUEST_EXAMPLE,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=PostCreateSerializer,
                description="게시글 등록 성공",
                examples=POST_CREATE_RESPONSE_EXAMPLE,
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="잘못된 요청"
            ),
        },
        auth=None,
        tags=["Posts"],
    )
    def post(self, request):
        serializer = PostCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            post = serializer.save()
            return Response(serializer.to_representation(post),
                            status=status.HTTP_201_CREATED)  # Todo: attach read serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(transaction.atomic, name='dispatch')
class PostDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'

    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method.
        - GET: Uses PostDetailSerializer for detailed representation.
        - PUT/PATCH: Uses PostUpdateSerializer for validation.
        - DELETE: Uses an empty PostDeleteSerializer.
        """
        if self.request.method in ['PATCH']:
            return PostUpdateSerializer
        elif self.request.method == 'GET':
            return PostReadSerializer
        return PostDeleteSerializer

    @extend_schema(
        summary="게시글 삭제",
        description="게시글을 soft delete 처리합니다. (is_deleted 플래그 설정)",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description="게시글 삭제 성공",
                examples=[OpenApiExample("Success Response", value={'detail': 'soft deleted'})]
            ),
            # status.HTTP_204_NO_CONTENT: OpenApiResponse(description="게시글 삭제 성공 (No Content)"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="게시글을 찾을 수 없음"),
        }
    )
    def destroy(self, request, *args, **kwargs):
        """ Overrides the default destroy action to perform a soft delete. """
        self.get_object().soft_delete()
        return Response({'detail': 'soft deleted'}, status=status.HTTP_204_NO_CONTENT)


class PresignedURLView(GenericAPIView):
    # """
    # Generates presigned URLs for S3.
    # This view does not perform any database operations, so it does not
    # require a transaction.
    # """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="게시글 이미지 업로  드 URL 생성",
        description="게시글 이미지 업로드 URL 생성을 요청합니다.",
        request=PresignedURLRequestSerializer,
        examples=PRESIGNED_POST_URL_REQUEST_EXAMPLE,
        responses={
            # status.HTTP_201_CREATED: OpenApiResponse(
            #     # response=PostCreateSerializer,
            #     description="게시글 등록 성공",
            #     examples=PRESIGNED_POST_URL_RESPONSE_EXAMPLE,
            # ),
            status.HTTP_200_OK: PRESIGNED_POST_URL_RESPONSE_EXAMPLE,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="잘못된 요청"
            ),
        },
        auth=None,
        tags=["Posts"],
    )
    def post(self, request):
        serializer = PresignedURLRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        files = serializer.validated_data['files']

        user_uid = request.user.uid

        results = []
        for file_info in files:
            file_name = file_info.get('file_name')
            presigned_url = create_presigned_post(
                settings.AWS_S3_MEDIA_BUCKET_NAME,
                build_object_name(user_uid, file_name),
                expiration=300
            )
            results.append({
                "file_name": file_name,
                "presigned_url": presigned_url,
            })

        return Response({"results": results})


class FeedMockListView(ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(MOCK_PRIVATE_FEED)
        else:
            return Response(MOCK_PUBLIC_FEED)
