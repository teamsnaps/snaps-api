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
from rest_framework.decorators import api_view
from rest_framework import status

from django.contrib.auth import get_user_model
from snapsapi.apps.core.models import Collection, CollectionMember

User = get_user_model()
from snapsapi.apps.core.serializers import (
    CollectionReadSerializer,
    CollectionWriteSerializer,
    CollectionMemberSerializer,
)
from snapsapi.apps.core.pagination import StandardResultsSetPagination


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


@method_decorator(transaction.atomic, name='dispatch')
class CollectionListCreateView(ListCreateAPIView):
    """
    List and create collections.
    - GET /api/collections/ - List collections
    - POST /api/collections/ - Create a new collection
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    read_serializer_class = CollectionReadSerializer
    write_serializer_class = CollectionWriteSerializer

    def get_queryset(self):
        """
        Return collections owned by the current user or where the user is a member.
        """
        user = self.request.user
        # 사용자 인증 확인 추가
        if not user.is_authenticated:
            return Collection.objects.none()

        # Get collections owned by the user
        owned_collections = Collection.objects.get_collections_by_user(user)
        # Get collections where the user is a member
        member_collections = Collection.objects.get_collections_with_membership(user)
        # Combine the querysets
        return (owned_collections | member_collections).distinct()


@method_decorator(transaction.atomic, name='dispatch')
class CollectionDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a collection.
    - GET /api/collections/{uid}/ - Retrieve a collection
    - PATCH /api/collections/{uid}/ - Update a collection
    - DELETE /api/collections/{uid}/ - Delete a collection
    """
    permission_classes = [IsAuthenticated]
    read_serializer_class = CollectionReadSerializer
    write_serializer_class = CollectionWriteSerializer
    lookup_field = 'uid'
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """
        Return collections owned by the current user or where the user is a member.
        """
        user = self.request.user
        # Get collections owned by the user
        owned_collections = Collection.objects.get_collections_by_user(user)
        # Get collections where the user is a member
        member_collections = Collection.objects.get_collections_with_membership(user)
        # Combine the querysets
        return (owned_collections | member_collections).distinct()

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete a collection.
        """
        collection = self.get_object()
        # Only the owner can delete a collection
        if collection.owner != request.user:
            return Response(
                {"detail": "You do not have permission to delete this collection."},
                status=status.HTTP_403_FORBIDDEN
            )
        collection.soft_delete()
        return Response({'detail': 'Collection soft deleted'}, status=status.HTTP_204_NO_CONTENT)


@method_decorator(transaction.atomic, name='dispatch')
class CollectionMemberView(GenericAPIView):
    """
    Add or remove members from a collection.
    - POST /api/collections/{uid}/members/{user_uid}/ - Add a member to a collection
    - DELETE /api/collections/{uid}/members/{user_uid}/ - Remove a member from a collection
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CollectionMemberSerializer
    lookup_field = 'uid'

    def get_collection(self):
        """
        Get the collection object.
        """
        uid = self.kwargs.get('uid')
        return Collection.objects.get(uid=uid)

    def post(self, request, *args, **kwargs):
        """
        Add a member to a collection.
        """
        collection = self.get_collection()
        # Only the owner can add members
        if collection.owner != request.user:
            return Response(
                {"detail": "You do not have permission to add members to this collection."},
                status=status.HTTP_403_FORBIDDEN
            )

        user_uid = kwargs.get('user_uid')
        try:
            user = User.objects.get(uid=user_uid)
        except User.DoesNotExist:
            return Response(
                {"detail": "User with this UID does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if the user is already a member
        if collection.members.filter(user=user).exists():
            return Response(
                {"detail": "User is already a member of this collection."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add the user as a member
        member = CollectionMember.objects.create(collection=collection, user=user)
        return Response(
            CollectionMemberSerializer(member).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        """
        Remove a member from a collection.
        """
        collection = self.get_collection()
        user_uid = kwargs.get('user_uid')

        # Only the owner can remove members
        if collection.owner != request.user:
            return Response(
                {"detail": "You do not have permission to remove members from this collection."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            user = User.objects.get(uid=user_uid)
        except User.DoesNotExist:
            return Response(
                {"detail": "User with this UID does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if the user is a member
        try:
            member = collection.members.get(user=user)
        except CollectionMember.DoesNotExist:
            return Response(
                {"detail": "User is not a member of this collection."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Remove the member
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(transaction.atomic, name='dispatch')
class CollectionAddPostView(GenericAPIView):
    """
    Add or remove posts from a collection.
    - POST /api/collections/{uid}/posts/{post_uid}/ - Add a post to a collection
    - DELETE /api/collections/{uid}/posts/{post_uid}/ - Remove a post from a collection
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'

    def get_collection(self):
        """
        Get the collection object.
        """
        uid = self.kwargs.get('uid')
        return Collection.objects.get(uid=uid)

    def post(self, request, *args, **kwargs):
        """
        Add a post to a collection.
        """
        collection = self.get_collection()
        post_uid = kwargs.get('post_uid')

        # Check if the user can add posts to this collection
        if not collection.can_user_add_posts(request.user):
            return Response(
                {"detail": "You do not have permission to add posts to this collection."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get the post by uid
        try:
            from snapsapi.apps.posts.models import Post
            post = Post.objects.get(uid=post_uid)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post with this UID does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if the post is already in the collection
        if collection.posts.filter(pk=post.pk).exists():
            return Response(
                {"detail": "Post is already in this collection."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add the post to the collection
        collection.posts.add(post)
        return Response(
            {"detail": "Post added to collection."},
            status=status.HTTP_200_OK
        )

    def delete(self, request, *args, **kwargs):
        """
        Remove a post from a collection.
        """
        collection = self.get_collection()
        post_uid = kwargs.get('post_uid')

        # Check if the user can remove posts from this collection
        if not collection.can_user_add_posts(request.user):
            return Response(
                {"detail": "You do not have permission to remove posts from this collection."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if the post is in the collection
        try:
            from snapsapi.apps.posts.models import Post
            post = collection.posts.get(uid=post_uid)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post is not in this collection."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Remove the post from the collection
        collection.posts.remove(post)
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(transaction.atomic, name='dispatch')
class DefaultCollectionAddPostView(GenericAPIView):
    """
    Toggle posts in the user's default collection.
    - POST /api/collections/posts/{post_uid}/ - Toggle a post in the default collection (add if not present, remove if present)
    """
    permission_classes = [IsAuthenticated]

    def get_default_collection(self, user):
        """
        Get the user's default collection.
        """
        try:
            return Collection.objects.filter(owner=user, name='default').first()
        except Collection.DoesNotExist:
            return None

    def post(self, request, *args, **kwargs):
        """
        Toggle a post in the user's default collection.
        If the post is already in the collection, it will be removed.
        If the post is not in the collection, it will be added.
        """
        # Get the user's default collection
        collection = self.get_default_collection(request.user)
        if not collection:
            return Response(
                {"detail": "Default collection not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        post_uid = kwargs.get('post_uid')

        # Get the post by uid
        try:
            from snapsapi.apps.posts.models import Post
            post = Post.objects.get(uid=post_uid)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post with this UID does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if the post is already in the collection
        if collection.posts.filter(pk=post.pk).exists():
            # Remove the post from the collection
            collection.posts.remove(post)
            return Response(
                {
                    "detail": "Post removed from default collection.",
                    "is_collected": False
                },
                status=status.HTTP_200_OK
            )
        else:
            # Add the post to the collection
            collection.posts.add(post)
            return Response(
                {
                    "detail": "Post added to default collection.",
                    "is_collected": True
                },
                status=status.HTTP_200_OK
            )
