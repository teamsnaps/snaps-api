import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from snapsapi.apps.core.models import Follow


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user1():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        email='user1@snaps.com', 
        password='mypassword', 
        username='user1'
    )
    return user


@pytest.fixture
def user2():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        email='user2@snaps.com', 
        password='mypassword', 
        username='user2'
    )
    return user


@pytest.fixture
def jwt_client(api_client, user1):
    refresh = RefreshToken.for_user(user1)
    access_token = str(refresh.access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return api_client


@pytest.fixture
def jwt_client_user2(api_client, user2):
    refresh = RefreshToken.for_user(user2)
    access_token = str(refresh.access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return api_client


@pytest.fixture
def follow_relation(user1, user2):
    """User1 follows User2"""
    follow = Follow.objects.create(
        follower=user1,
        following=user2
    )
    return follow