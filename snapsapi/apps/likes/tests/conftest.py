import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from snapsapi.apps.posts.models import Post
from snapsapi.apps.comments.models import Comment
from snapsapi.apps.likes.models import PostLike, CommentLike


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
def post1(user1):
    post = Post.objects.create(
        user=user1,
        caption="test post for likes",
        is_deleted=False,
        is_active=True,
    )
    return post


@pytest.fixture
def comment1(user1, post1):
    comment = Comment.objects.create(
        user=user1,
        post=post1,
        content="This is a test comment for likes",
        is_deleted=False
    )
    return comment


@pytest.fixture
def post_like(user1, post1):
    like = PostLike.objects.create(
        user=user1,
        post=post1
    )
    return like


@pytest.fixture
def comment_like(user1, comment1):
    like = CommentLike.objects.create(
        user=user1,
        comment=comment1
    )
    return like