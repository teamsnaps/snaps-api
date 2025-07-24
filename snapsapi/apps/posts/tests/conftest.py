import pytest

from django.contrib.auth import get_user_model
from rest_framework.authtoken import models as am
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from snapsapi.apps.posts import models as m


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user1():
    user_model = get_user_model()
    user = user_model.objects.create_user(email='user1@snaps.com', password='mypassword', username='user1')
    user.save()
    return user


@pytest.fixture
def user2():
    user_model = get_user_model()
    user = user_model.objects.create_user(email='user2@snaps.com', password='mypassword', username='user2')
    user.save()


@pytest.fixture
def superuser1():
    user_model = get_user_model()
    user = user_model.objects.create_superuser(
        'superuser1', 'superuser1@snaps.com', 'mypassword')
    user.last_name = 'konan'
    am.Token.objects.get_or_create(user=user)
    return user


@pytest.fixture
def tag1():
    return m.Tag.objects.create(name="testtag", is_featured=True)


@pytest.fixture
def post_image1(tag1):
    return m.PostImage.objects.create(
        url="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
        order=0,
        post=None
    )


@pytest.fixture
def post_of_user1(user1, tag1):
    post = m.Post.objects.create(
        user=user1,
        caption="test caption",
        is_deleted=False,
        is_active=True,
    )
    # post.images.set(post_image1)
    post.tags.add(tag1)
    m.PostImage.objects.create(
        post=post,
        url="https://example.com/image.png",
        order=0
    )

    return post


@pytest.fixture
def post1(user1, tag1):
    post = m.Post.objects.create(
        user=user1,
        caption="test caption",
        is_deleted=False,
        is_active=True,
    )
    post.tags.add(tag1)
    m.PostImage.objects.create(
        post=post,
        url="https://example.com/image.png",
        order=0
    )

    return post


@pytest.fixture
def post2(user1, tag1):
    post = m.Post.objects.create(
        user=user1,
        caption="test caption",
        images=[],
        is_deleted=True,
        is_active=False,
    )
    post.tags.add(tag1)
    return post


@pytest.fixture
def post3(user1, tag1):
    post = m.Post.objects.create(
        user=user1,
        caption="test caption",
        images=[],
        is_deleted=True,
        is_active=True,
    )
    post.tags.add(tag1)
    return post


@pytest.fixture
def post4(user1, tag1):
    post = m.Post.objects.create(
        user=user1,
        caption="test caption",
        images=[],
        is_deleted=False,
        is_active=False,
    )
    post.tags.add(tag1)
    return post


@pytest.fixture
def jwt_client(api_client, user1):
    # 1) RefreshToken.for_user()로 토큰 생성
    refresh = RefreshToken.for_user(user1)
    access_token = str(refresh.access_token)
    # 2) Authorization 헤더에 Bearer 토큰 설정
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return api_client


@pytest.fixture
def jwt_client_user1(api_client, user1):
    # 1) RefreshToken.for_user()로 토큰 생성
    refresh = RefreshToken.for_user(user1)
    access_token = str(refresh.access_token)
    # 2) Authorization 헤더에 Bearer 토큰 설정
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return api_client


@pytest.fixture
def invalid_jwt_client(api_client):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer 123456abcdef7890')
    return api_client