import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from snapsapi.apps.core.models import Follow, Collection, CollectionMember
from snapsapi.apps.posts.models import Post, Tag, PostImage


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


@pytest.fixture
def tag1():
    """A test tag"""
    return Tag.objects.create(name="testtag", is_featured=True)


@pytest.fixture
def post1(user1, tag1):
    """A test post by user1"""
    post = Post.objects.create(
        user=user1,
        caption="test caption",
        is_deleted=False,
        is_active=True,
    )
    post.tags.add(tag1)
    PostImage.objects.create(
        post=post,
        url="https://example.com/image.png",
        order=0
    )
    return post


@pytest.fixture
def collection1(user1):
    """A public collection owned by user1"""
    collection = Collection.objects.create(
        name="Test Collection",
        description="A test collection",
        owner=user1,
        is_public=True
    )
    return collection


@pytest.fixture
def private_collection(user1):
    """A private collection owned by user1"""
    collection = Collection.objects.create(
        name="Private Collection",
        description="A private test collection",
        owner=user1,
        is_public=False
    )
    return collection


@pytest.fixture
def collection_user2(user2):
    """A collection owned by user2"""
    collection = Collection.objects.create(
        name="User2's Collection",
        description="A collection owned by user2",
        owner=user2,
        is_public=True
    )
    return collection


@pytest.fixture
def default_collection(user1):
    """User1's default collection"""
    collection = Collection.objects.create(
        name="default",
        description="Default collection",
        owner=user1,
        is_public=True
    )
    return collection


@pytest.fixture
def collection_member(collection_user2, user1):
    """User1 is a member of user2's collection"""
    member = CollectionMember.objects.create(
        collection=collection_user2,
        user=user1
    )
    return member


@pytest.fixture
def collection_with_post(collection1, post1):
    """A collection with a post"""
    collection1.posts.add(post1)
    return collection1