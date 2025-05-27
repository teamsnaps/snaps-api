from django.conf import settings
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.views import APIView


class SocialRegisterView(SocialLoginView):
    callback_url = settings.GOOGLE_OAUTH2_REDIRECT_URL
    client_class = OAuth2Client

    # noinspection PyAttributeOutsideInit
    def set_adapter_class(self, provider):
        if provider == 'google':
            self.adapter_class = GoogleOAuth2Adapter
        elif provider == 'kakao':
            self.adapter_class = KakaoOAuth2Adapter
        elif provider == 'naver':
            self.adapter_class = NaverOAuth2Adapter
        else:
            raise Exception('Unsupported provider')

    def post(self, request, *args, **kwargs):
        provider = request.data.get('provider')
        self.set_adapter_class(provider)
        return super().post(request, *args, **kwargs)
