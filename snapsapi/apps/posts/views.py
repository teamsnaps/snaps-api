from django.conf import settings
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from drf_rw_serializers.generics import (
    GenericAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    ListCreateAPIView
)
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from snapsapi.apps.posts import serializers as s

from snapsapi.apps.posts.serializers import (
    PostReadSerializer,
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
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    read_serializer_class = s.PostReadSerializer
    write_serializer_class = s.PostWriteSerializer

    def get_queryset(self):
        queryset = (
            Post.objects.filter(is_deleted=False)
            .prefetch_related(
                'user__profile',
                'images',
                'tags'
            )
            .order_by('-created_at')
        )

        tag_query = self.request.query_params.get('tag', None)

        if tag_query:
            queryset = queryset.filter(
                tags__name__icontains=tag_query
            ).distinct()

        return queryset

    # @extend_schema(
    #     summary=_("Create New Post"),
    #     description=_("Users can create a new post through this endpoint. Posts can include multiple images, caption (content), and tags."),
    #     request=PostCreateSerializer,
    #     examples=POST_CREATE_REQUEST_EXAMPLE,
    #     responses={
    #         status.HTTP_201_CREATED: OpenApiResponse(
    #             response=PostReadSerializer,
    #             description=_("Post created successfully. The response body includes detailed information about the created post."),
    #             examples=POST_CREATE_RESPONSE_EXAMPLE,
    #         ),
    #         status.HTTP_400_BAD_REQUEST: OpenApiResponse(
    #             description=_("Invalid request format. This error may occur if required fields are missing or data format is incorrect.")
    #         ),
    #     },
    #     tags=["Posts"],
    # )
    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data, context={"request": request})
    #     if serializer.is_valid(raise_exception=True):
    #         created_instance = serializer.save()
    #         read_serializer = PostReadSerializer(created_instance, context=self.get_serializer_context())
    #         headers = self.get_success_headers(read_serializer.data)
    #         return Response(read_serializer.data, status=status.HTTP_201_CREATED,
    #                         headers=headers)  # Todo: attach drf_rw_serializers serializer
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(transaction.atomic, name='dispatch')
class PostDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticatedOrReadOnly]
    read_serializer_class = s.PostReadSerializer
    write_serializer_class = s.PostWriteSerializer
    lookup_field = 'uid'

    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    # def get_serializer_class(self):
    #     """
    #     Returns the appropriate serializer class based on the request method.
    #     - GET: Uses PostDetailSerializer for detailed representation.
    #     - PUT/PATCH: Uses PostCreateSerializer for validation.
    #     - DELETE: Uses an empty PostDeleteSerializer.
    #     """
    #     if self.request.method in ['PATCH']:
    #         return s.PostWriteSerializer
    #     elif self.request.method == 'GET':
    #         return PostReadSerializer
    #     return PostDeleteSerializer

    @extend_schema(
        summary="Delete Post",
        description="Soft delete a post (sets the is_deleted flag)",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description="Post deleted successfully",
                examples=[OpenApiExample("Success Response", value={'detail': 'soft deleted'})]
            ),
            # status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Post deleted successfully (No Content)"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Post not found"),
        }
    )
    def destroy(self, request, *args, **kwargs):
        """ Overrides the default destroy action to perform a soft delete. """
        self.get_object().soft_delete()
        return Response({'detail': 'soft deleted'}, status=status.HTTP_204_NO_CONTENT)


class PostImageUploadURLView(GenericAPIView):
    """
    Generates presigned URLs for S3 to upload post images.
    This view does not perform any database operations, so it does not
    require a transaction.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Generate Post Image Upload URL",
        description="Request to generate a URL for uploading post images.",
        request=PresignedURLRequestSerializer,
        examples=PRESIGNED_POST_URL_REQUEST_EXAMPLE,
        responses={
            # status.HTTP_201_CREATED: OpenApiResponse(
            #     # response=PostCreateSerializer,
            #     description="Post registration successful",
            #     examples=PRESIGNED_POST_URL_RESPONSE_EXAMPLE,
            # ),
            status.HTTP_200_OK: PRESIGNED_POST_URL_RESPONSE_EXAMPLE,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid request"
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
                expiration=settings.AWS_S3_PRESIGNED_URL_POST_EXPIRATION
            )
            results.append({
                "file_name": file_name,
                "presigned_url": presigned_url,
            })

        return Response({"results": results}, status=status.HTTP_200_OK)

# This class is deprecated and should not be used.
# Use the tag filtering in PostListCreateView.get_queryset() instead.
# class PostSearchView(ListAPIView):
#     """
#     Search for posts by tag name passed as a query parameter.
#     - GET /api/posts/search/?tag=search_term
#     """
#     serializer_class = s.PostReadSerializer
#     permission_classes = [AllowAny]  # Anyone can search
#
#     def get_queryset(self):
#         """
#         If 'tag' query parameter exists, search for posts containing that tag.
#         """
#         tag_query = self.request.query_params.get('tag', None)
#
#         if tag_query:
#             # Assumes the Post model is connected to the Tag model through a ManyToManyField named 'tags',
#             # and that the Tag model has a 'name' field.
#             # Using distinct() to prevent duplicate posts from being returned.
#             return Post.objects.filter(
#                 tags__name__icontains=tag_query
#             ).distinct()
#
#         # Return an empty queryset if there's no search term.
#         return Post.objects.none()
