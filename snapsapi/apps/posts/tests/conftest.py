import pytest

from django.contrib.auth import get_user_model
from rest_framework.authtoken import models as am
from rest_framework.test import APIClient
from snapsapi.apps.core import models as m


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user1():
    user_model = get_user_model()
    user = user_model.objects.create_user(username='user1', password='mypassword')
    user.save()
    return user


@pytest.fixture
def user2():
    user_model = get_user_model()
    user = user_model.objects.create_user(username='user2', password='mypassword')
    user.save()


@pytest.fixture
def superuser1():
    user_model = get_user_model()
    user = user_model.objects.create_superuser(
        'superuser1', 'superuser1@snaps.com', 'mypassword')
    user.last_name = 'conan'
    am.Token.objects.get_or_create(user=user)
    return user


@pytest.fixture
def tag1():
    return m.Tag.objects.create(name="testtag")


@pytest.fixture
def post1(user1, tag1):
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
        is_deleted=False,
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
