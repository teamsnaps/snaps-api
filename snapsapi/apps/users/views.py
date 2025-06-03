
from django.conf import settings
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import (
    SocialLoginView as _SocialLoginView,
    SocialConnectView as _SocialConnectView
)
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view, inline_serializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from rest_framework import serializers as s
from snapsapi.apps.users.schemas import *

from snapsapi.apps.users.serializers import (
    SocialLoginWriteSerializer,
    SocialLoginReadSerializer,
    SocialLoginResponseSerializer,
)


class SocialLoginView(_SocialLoginView):
    callback_url = settings.GOOGLE_OAUTH2_REDIRECT_URL
    client_class = OAuth2Client
    serializer_class = None

    PROVIDER_ADAPTERS = {
        'google': GoogleOAuth2Adapter,
        # 'kakao': KakaoOAuth2Adapter,
        # 'naver': NaverOAuth2Adapter,
    }
    CALLBACK_URLS = {
        'google': settings.GOOGLE_OAUTH2_REDIRECT_URL,
        'kakao': settings.GOOGLE_OAUTH2_REDIRECT_URL,
        'naver': settings.GOOGLE_OAUTH2_REDIRECT_URL,
    }

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SocialLoginWriteSerializer
        return super().get_serializer_class()

    @extend_schema(
        operation_id="social_login",
        summary="소셜 회원가입 / 로그인",
        description="provider와 access_token을 받아서 소셜 회원가입/로그인 처리를 수행합니다.",
        request=inline_serializer(
            name="SocialLoginInlineRequest",
            fields={
                "access_token": s.CharField(help_text="소셜 플랫폼에서 발급받은 액세스 토큰"),
                "provider": s.ChoiceField(choices=['google', 'kakao', 'naver'],
                                          help_text="사용할 소셜 로그인 제공자 (google, kakao, naver 중 하나)"),
            }

        ),
        examples=SOCIAL_LOGIN_REQUEST_EXAMPLE,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=SocialLoginResponseSerializer,
                examples=USER_REGISTRATION_RESPONSE_EXAMPLE,
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
                    f"'{provider}' is not a supported provider. Choose one of: {', '.join(self.PROVIDER_ADAPTERS.keys())}."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.adapter_class = adapter_class
        self.callback_url = callback_url
        return super().post(request, *args, **kwargs)


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
