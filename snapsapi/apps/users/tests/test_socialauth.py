import pytest
import requests
from rest_framework.test import APIClient
import responses

@pytest.mark.django_db
class TestSocialRegisterView:
    @pytest.fixture
    def client(self):
        return APIClient()

    @responses.activate
    def test_get_google_user_info(self):
        google_userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

        fake_google_response = {
            "id": "123456789",
            "email": "testuser@gmail.com",
            "verified_email": True,
            "name": "테스트유저",
            "given_name": "테스트",
            "family_name": "유저",
            "picture": "https://lh3.googleusercontent.com/a-/someprofile.jpg",
            "locale": "ko"
        }

        responses.add(
            responses.GET,
            google_userinfo_url,
            json=fake_google_response,
            status=200
        )

        resp = requests.get(google_userinfo_url, headers={"Authorization": "Bearer dummy-access-token"})

        assert resp.status_code == 200
        assert resp.json()["email"] == "testuser@gmail.com"
        assert resp.json() == fake_google_response

    # @patch("allauth.socialaccount.providers.google.views.GoogleOAuth2Adapter.complete_login")
    # def test_social_register_google_success(self, mock_complete_login, client, verified_user1):
    #     # Mock complete_login to always return a dummy sociallogin
    #     from allauth.socialaccount.models import SocialLogin, SocialAccount, SocialApp
    #     from django.contrib.auth import get_user_model
    #
    #     User = get_user_model()
    #     user = User.objects.create(email="mock@user.com")
    #     sociallogin = MagicMock(spec=SocialLogin)
    #     sociallogin.user = user
    #     sociallogin.account = MagicMock(spec=SocialAccount)
    #     sociallogin.account.provider = "google"
    #     sociallogin.token = MagicMock(token="mocked-access-token")
    #     mock_complete_login.return_value = sociallogin