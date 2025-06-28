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
        summary="소셜 회원가입 / 로그인",
        description="provider와 access_token을 받아서 소셜 회원가입/로그인 처리를 수행합니다.",
        request=inline_serializer(
            name="SocialLoginInlineRequest",
            fields={
                "access_token": serializers.CharField(help_text="소셜 플랫폼에서 발급받은 액세스 토큰"),
                "provider": serializers.ChoiceField(choices=['google', 'kakao', 'naver'],
                                                    help_text="사용할 소셜 로그인 제공자 (google, kakao, naver 중 하나)"),
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
                {"detail": "OAuth2 인증에 실패했습니다. 유효한 access_token을 제공해주세요."},
                status=status.HTTP_400_BAD_REQUEST
            )


class FollowToggleView(APIView):
    """
    특정 유저에 대한 팔로우/언팔로우를 처리하는 토글 방식의 View입니다.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # URL에서 팔로우할 대상 유저의 uid를 가져옵니다.
        follower = request.user

        user_to_follow_uid = self.kwargs.get('user_uid')
        following = User.objects.get_user_by_uid(uid=user_to_follow_uid)

        # get_or_create를 사용하여 팔로우 관계를 가져오거나 생성합니다.
        # created는 새로 생성되었으면 True, 이미 존재했으면 False를 반환합니다.
        follow, created = Follow.objects.follow(
            follower=follower,
            following=following
        )

        if not created:
            # 이미 팔로우 관계가 존재했다면, 삭제하여 '언팔로우'를 수행합니다.
            Follow.objects.unfollow(
                follower=follower,
                following=following
            )

        # DB에서 최신 카운트 정보를 가져오기 위해 객체를 새로고침합니다.
        following.refresh_from_db()

        serializer = s.FollowResponseSerializer({
            'is_following': created,  # 생성되었으면 True(팔로우 성공), 아니면 False(언팔로우 성공)
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


class UserProfileImagePresignedURLView(GenericAPIView):
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


class GoogleConnectView(_SocialConnectView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    # # noinspection PyAttributeOutsideInit
    # def set_adapter_class(self, provider: str):
    #     if provider == 'google':
    #         self.adapter_class = GoogleOAuth2Adapter
    #     elif provider == 'kakao':
    #         self.adapter_class = KakaoOAuth2Adapter
    #     elif provider == 'naver':
    #         self.adapter_class = NaverOAuth2Adapter
    #     else:
    #         print(provider)
    #         raise Exception('Unsupported provider')

    # def post(self, request, *args, **kwargs):
    #     print("Request Data:", request.data)  # 디버깅 정보 출력
    #     # provider = request.data.get('provider')
    #     # self.set_adapter_class(provider)
    #     # request.data.pop('provider')
    #     print("Request Data:", request.data)  # 디버깅 정보 출력
    #     print("Adapter Class:", self.adapter_class)  # 확인용 debug 출력
    #
    #     return super().post(request, *args, **kwargs)
