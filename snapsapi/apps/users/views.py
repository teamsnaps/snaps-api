from django.conf import settings
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView, SocialConnectView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import json

class SocialRegisterView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH2_REDIRECT_URL
    client_class = OAuth2Client

# class SocialRegisterView(SocialLoginView):
#     callback_url = settings.GOOGLE_OAUTH2_REDIRECT_URL
#     client_class = OAuth2Client
#
#     # provider 이름과 Adapter 매핑
#     PROVIDER_ADAPTERS = {
#         'google': GoogleOAuth2Adapter,
#         'kakao': KakaoOAuth2Adapter,
#         'naver': NaverOAuth2Adapter,
#     }


    # def get_adapter_class(self):
    #     # POST, application/json 등 모든 경우 지원
    #     if self.request.content_type == "application/json":
    #         try:
    #             body_data = json.loads(self.request.body)
    #             provider = body_data.get('provider')
    #         except Exception:
    #             provider = None
    #     else:
    #         provider = self.request.POST.get('provider')
    #     adapter_class = self.PROVIDER_ADAPTERS.get(provider)
    #     if not adapter_class:
    #         raise self.provider_error(provider)
    #     return adapter_class


    # def provider_error(self, provider):
    #     from rest_framework.exceptions import ValidationError
    #     valid = ', '.join(self.PROVIDER_ADAPTERS.keys())
    #     return ValidationError({
    #         "provider": [f"'{provider}' is not a supported provider. Choose one of: {valid}."]
    #     })

    # def post(self, request, *args, **kwargs):
    #     provider = request.data.get('provider')
    #     adapter_class = self.PROVIDER_ADAPTERS.get(provider)
    #     if not adapter_class:
    #         return Response(
    #             {"provider": [f"'{provider}' is not a supported provider. Choose one of: {', '.join(self.PROVIDER_ADAPTERS.keys())}."]},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     self.adapter_class = adapter_class
    #     return super().post(request, *args, **kwargs)


class GoogleConnectView(SocialConnectView):
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
