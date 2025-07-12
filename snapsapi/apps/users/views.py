from django.conf import settings
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error
from dj_rest_auth.registration.views import (
    SocialLoginView as _SocialLoginView,
    SocialConnectView as _SocialConnectView
)
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view, inline_serializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from rest_framework import serializers

from drf_rw_serializers.generics import ListAPIView, UpdateAPIView, GenericAPIView, RetrieveAPIView

from snapsapi.apps.users.models import Profile
from snapsapi.apps.core.models import Follow
from snapsapi.apps.users.schemas import *
from snapsapi.apps.users.permissions import IsProfileOwner, IsActiveUser

from snapsapi.apps.users import serializers as s

# from snapsapi.apps.users.serializers import (
#     SocialLoginWriteSerializer,
#     SocialLoginReadSerializer,
#     SocialLoginResponseSerializer,
#     FollowResponseSerializer,
#     UsernameUpdateSerializer, UserProfileSerializer, UserProfileImageFileInfoSerializer,
#     UserProfileUpdateSerializer
# )
from snapsapi.utils.aws import create_presigned_post, build_user_profile_image_object_name

User = get_user_model()


class SocialLoginView(_SocialLoginView):
    callback_url = settings.GOOGLE_REDIRECT_URL
    client_class = OAuth2Client
    serializer_class = None
    queryset = User.objects.filter(is_active=True, is_deleted=False)

    PROVIDER_ADAPTERS = {
        'google': GoogleOAuth2Adapter,
        'kakao': KakaoOAuth2Adapter,
        'naver': NaverOAuth2Adapter,
    }
    CALLBACK_URLS = {
        'google': settings.GOOGLE_REDIRECT_URL,
        'kakao': settings.GOOGLE_REDIRECT_URL,
        'naver': settings.GOOGLE_REDIRECT_URL,
    }

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return s.SocialLoginWriteSerializer
        return super().get_serializer_class()

    @extend_schema(
        operation_id="social_login",
        summary="Social Registration / Login",
        description="Processes social registration/login by receiving provider and access_token.",
        request=inline_serializer(
            name="SocialLoginInlineRequest",
            fields={
                "access_token": serializers.CharField(help_text="Access token issued by the social platform"),
                "provider": serializers.ChoiceField(choices=['google', 'kakao', 'naver'],
                                                    help_text="Social login provider to use (one of: google, kakao, naver)"),
            }

        ),
        examples=SOCIAL_LOGIN_REQUEST_EXAMPLE,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=s.SocialLoginResponseSerializer,
                examples=USER_REGISTRATION_RESPONSE_EXAMPLE,
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=inline_serializer(
                    name="SocialLoginErrorResponse",
                    fields={
                        "detail": serializers.CharField(),
                    }),
                examples=USER_REGISTRATION_RESPONSE_ERROR_EXAMPLE,
            )
        },
        auth=None,
        tags=["Users"],
    )
    def post(self, request, *args, **kwargs):
        provider = request.data.get('provider')
        adapter_class = self.PROVIDER_ADAPTERS.get(provider)
        callback_url = self.CALLBACK_URLS.get(provider)
        if not adapter_class:
            return Response(
                {"provider": [
                    f"'{provider}' is not a supported provider. Please choose one of: [{', '.join(self.PROVIDER_ADAPTERS.keys())}]"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.adapter_class = adapter_class
        self.callback_url = callback_url
        try:
            return super().post(request, *args, **kwargs)
        except OAuth2Error as e:
            return Response(
                {"detail": "OAuth2 authentication failed. Please provide a valid access_token."},
                status=status.HTTP_400_BAD_REQUEST
            )


class FollowToggleView(APIView):
    """
    A toggle-style View that handles follow/unfollow actions for a specific user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get the uid of the target user to follow from the URL
        follower = request.user

        user_to_follow_uid = self.kwargs.get('user_uid')
        following = User.objects.get_user_by_uid(uid=user_to_follow_uid)

        # Use follow method to get or create a follow relationship
        # 'created' returns True if newly created, False if it already existed
        follow, created = Follow.objects.follow(
            follower=follower,
            following=following
        )

        if not created:
            # If the follow relationship already exists, delete it to perform 'unfollow'
            Follow.objects.unfollow(
                follower=follower,
                following=following
            )

        # Refresh the object to get the latest count information from the database
        following.refresh_from_db()

        serializer = s.FollowResponseSerializer({
            'is_following': created,  # True if created (follow successful), False if not (unfollow successful)
            'followers_count': following.followers_count,
            'following_count': following.following_count
        })

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileView(RetrieveAPIView):
    queryset = User.objects.filter(is_active=True, is_deleted=False)
    serializer_class = s.UserProfileSerializer

    lookup_field = 'uid'
    lookup_url_kwarg = 'user_uid'


class UsernameUpdateView(UpdateAPIView):
    """
    Updates the username for the authenticated user. (PATCH)
    """
    permission_classes = [IsAuthenticated]
    write_serializer_class = s.UsernameUpdateSerializer
    read_serializer_class = s.UserSerializer

    def get_object(self):
        """
        Returns the object the view will be acting upon.
        Instead of looking up an ID from the URL, it always returns
        the user who made the request (request.user).
        """
        return self.request.user


class ProfileImageUploadURLView(GenericAPIView):
    """
    Generates presigned URLs for S3 to upload profile images.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = s.UserProfileImageFileInfoSerializer

    def post(self, request):
        file_name = request.data['file_name']
        user_uid = request.user.uid
        presigned_url = create_presigned_post(
            settings.AWS_S3_MEDIA_BUCKET_NAME,
            build_user_profile_image_object_name(user_uid, file_name),
            expiration=settings.AWS_S3_PRESIGNED_URL_POST_EXPIRATION
        )
        return Response({
            "file_name": file_name,
            "presigned_url": presigned_url,
        }, status=status.HTTP_200_OK)


class UserProfileUpdateView(UpdateAPIView):
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated, IsProfileOwner, IsActiveUser]
    serializer_class = s.UserProfileUpdateSerializer

    # read_serializer_class = s.UserSerializer

    def get_object(self):
        obj = self.queryset.get(user=self.request.user)
        return obj


class UserSearchView(ListAPIView):
    """
    Searches for users by username passed as a query parameter.
    - GET /api/users/search/?username=search_term
    """
    serializer_class = s.UserSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can search

    def get_queryset(self):
        """
        If the 'username' query parameter exists, searches for all users
        whose usernames contain the search term (case-insensitive) using the username__icontains filter.
        """
        username_query = self.request.query_params.get('username', None)

        if username_query:
            # Find users whose username field contains the search term (icontains)
            # Exclude the current user from search results using exclude(pk=self.request.user.pk)
            return User.objects.filter(
                username__icontains=username_query
            ).exclude(pk=self.request.user.pk)

        # Return an empty queryset if there's no search term
        return User.objects.none()


class SocialConnectView(_SocialConnectView):
    """
    View for connecting social accounts to an existing user account.
    Currently only supports Google, but can be extended to support other providers.
    """
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


class UserFollowListView(ListAPIView):
    """
    Lists followers or following users for a specific user.
    - GET /api/users/<user_uid>/connections/?type=followers - Lists users who follow the specified user
    - GET /api/users/<user_uid>/connections/?type=following - Lists users the specified user is following
    """
    serializer_class = s.UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Returns a queryset of users based on the 'type' query parameter:
        - 'followers': returns users who follow the specified user
        - 'following': returns users the specified user is following
        """
        user_uid = self.kwargs.get('user_uid')
        connection_type = self.request.query_params.get('type', 'followers')

        try:
            user = User.objects.get_user_by_uid(uid=user_uid)
        except:
            return User.objects.none()

        if connection_type == 'followers':
            # Get users who follow the specified user
            follower_relations = Follow.objects.filter(following=user)
            return User.objects.filter(id__in=follower_relations.values('follower_id'))
        elif connection_type == 'following':
            # Get users the specified user is following
            following_relations = Follow.objects.filter(follower=user)
            return User.objects.filter(id__in=following_relations.values('following_id'))
        else:
            return User.objects.none()
