from django.conf import settings
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from snapsapi.apps.posts.serializers import (
    PostCreateSerializer,
    PostReadSerializer,
    PostUpdateSerializer,
    PostDeleteSerializer,
    PresignedURLRequestSerializer,
)
from snapsapi.apps.posts.schemas import (
    POST_CREATE_REQUEST_EXAMPLE,
    POST_CREATE_RESPONSE_EXAMPLE,
    PRESIGNED_POST_URL_RESPONSE_EXAMPLE,
    PRESIGNED_POST_URL_REQUEST_EXAMPLE,
)
from snapsapi.apps.core.pagination import StandardResultsSetPagination
from snapsapi.apps.posts.models import Post
from snapsapi.utils.aws import create_presigned_post, build_posts_image_object_name


@method_decorator(transaction.atomic, name='dispatch')
class PostListCreateView(ListCreateAPIView):
    # """
    # Handles the creation of a new post.
    # The entire process is wrapped in a database transaction. If any part of the
    # post creation fails (e.g., attaching images or tags), the entire transaction
    # will be rolled back, ensuring data consistency.
    # """
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return (
            Post.objects.filter(is_deleted=False)
            # .annotate(
            #     likes_count=Count('likes', distinct=True),
            #     comments_count=Count('comments', distinct=True))
            .prefetch_related(
                'user__profile',
                'images',
                'tags'
            )
            .order_by('-created_at')
        )

    def get_serializer_class(self):
        return PostCreateSerializer if self.request.method == 'POST' else PostReadSerializer

    @extend_schema(
        summary=_("새 게시글 작성"),
        description=_("사용자는 이 엔드포인트를 통해 새로운 게시글을 작성할 수 있습니다. 게시글에는 여러 개의 이미지, 캡션(내용), 그리고 태그를 포함할 수 있습니다."),
        request=PostCreateSerializer,
        examples=POST_CREATE_REQUEST_EXAMPLE,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=PostReadSerializer,
                description=_("게시글이 성공적으로 생성되었습니다. 응답 본문에는 생성된 게시글의 상세 정보가 포함됩니다."),
                examples=POST_CREATE_RESPONSE_EXAMPLE,
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description=_("요청 형식이 올바르지 않습니다. 필수 필드가 누락되었거나 데이터 형식이 잘못된 경우 이 오류가 발생할 수 있습니다.")
            ),
        },
        tags=["Posts"],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            created_instance = serializer.save()
            read_serializer = PostReadSerializer(created_instance, context=self.get_serializer_context())
            headers = self.get_success_headers(read_serializer.data)
            return Response(read_serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)  # Todo: attach drf_rw_serializers serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(transaction.atomic, name='dispatch')
class PostDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticatedOrReadOnly]
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
                build_posts_image_object_name(user_uid, file_name),
                expiration=300
            )
            results.append({
                "file_name": file_name,
                "presigned_url": presigned_url,
            })

        return Response({"results": results})
