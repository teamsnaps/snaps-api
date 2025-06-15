from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import boto3
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from snapsapi.apps.posts.serializers import PostCreateSerializer, PresignedURLRequestSerializer, PostUpdateSerializer
from snapsapi.apps.posts.schemas import (
    POST_CREATE_REQUEST_EXAMPLE,
    POST_CREATE_RESPONSE_EXAMPLE,
    PRESIGNED_POST_URL_RESPONSE_EXAMPLE,
    PRESIGNED_POST_URL_REQUEST_EXAMPLE,
)

from snapsapi.apps.posts.utils import create_presigned_post, build_object_name
from drf_rw_serializers.generics import GenericAPIView
from snapsapi.apps.posts.models import Post
from django.db import transaction

class PostCreateView(GenericAPIView):
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


# @transaction.atomic
class PostUpdateView(UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'

class PresignedURLView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="게시글 이미지 업로드 URL 생성",
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


class PostDeleteView(UpdateAPIView):
    queryset = Post.objects.filter(is_deleted=False)
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        post.is_deleted = True  # flag 변경
        post.save()
        return Response({'detail': 'soft deleted'}, status=status.HTTP_200_OK)