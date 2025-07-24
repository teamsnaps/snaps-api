import pytest
from django.urls import reverse
from rest_framework import status
from .payloads import CREATE_POST_PAYLOAD, UPDATED_POST_PAYLOAD


@pytest.mark.django_db
class TestPostListCreateView:
    """/api/posts/ 엔드포인트에 대한 테스트"""

    # def test_list_posts(self, client, post_of_user1):
    #     """GET /api/posts/ - 게시물 목록 조회를 테스트합니다."""
    #     url = reverse('posts:posts-list-create')
    #     res = client.get(url)
    #     assert res.status_code == status.HTTP_200_OK
    #     # 응답 데이터에 post_of_user1이 포함되어 있는지 확인할 수 있습니다.
    #     assert len(res.data) > 0

    def test_list_posts_with_keyword_search(self, client, user1, tag1):
        """GET /api/posts/?keyword=... - 키워드로 게시물 검색을 테스트합니다."""
        # Create posts with different captions
        from snapsapi.apps.posts.models import Post, PostImage, Tag

        # Create a new tag for testing
        tag2 = Tag.objects.create(name="pythontag", is_featured=True)

        # Post with caption containing "hello world"
        post1 = Post.objects.create(
            user=user1,
            caption="hello world test post",
            is_deleted=False,
            is_active=True,
        )
        post1.tags.add(tag1)
        PostImage.objects.create(
            post=post1,
            url="https://example.com/image1.png",
            order=0
        )

        # Post with caption containing "python django"
        post2 = Post.objects.create(
            user=user1,
            caption="python django test post",
            is_deleted=False,
            is_active=True,
        )
        post2.tags.add(tag2)
        PostImage.objects.create(
            post=post2,
            url="https://example.com/image2.png",
            order=0
        )

        # Test searching for "hello"
        url = reverse('posts:posts-list-create')
        res = client.get(f"{url}?keyword=hello")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data['count'] == 1
        assert data['results'][0]['caption'] == "hello world test post"

        # Test searching for "python"
        res = client.get(f"{url}?keyword=python")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data['count'] == 1
        assert data['results'][0]['caption'] == "python django test post"

        # Test searching for "test" (should return both posts)
        res = client.get(f"{url}?keyword=test")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data['count'] == 2

        # Test searching for non-existent keyword
        res = client.get(f"{url}?keyword=nonexistent")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data['count'] == 0

    def test_list_posts_with_tag_search(self, client, user1, tag1):
        """GET /api/posts/?tag=... - 태그로 게시물 검색을 테스트합니다."""
        # Create posts with different tags
        from snapsapi.apps.posts.models import Post, PostImage, Tag

        # Create a new tag for testing
        tag2 = Tag.objects.create(name="pythontag", is_featured=True)

        # Post with tag1
        post1 = Post.objects.create(
            user=user1,
            caption="post with tag1",
            is_deleted=False,
            is_active=True,
        )
        post1.tags.add(tag1)
        PostImage.objects.create(
            post=post1,
            url="https://example.com/image1.png",
            order=0
        )

        # Post with tag2
        post2 = Post.objects.create(
            user=user1,
            caption="post with tag2",
            is_deleted=False,
            is_active=True,
        )
        post2.tags.add(tag2)
        PostImage.objects.create(
            post=post2,
            url="https://example.com/image2.png",
            order=0
        )

        # Test searching for tag1
        url = reverse('posts:posts-list-create')
        res = client.get(f"{url}?tag={tag1.name}")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data['count'] == 1
        assert data['results'][0]['caption'] == "post with tag1"

        # Test searching for tag2
        res = client.get(f"{url}?tag={tag2.name}")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data['count'] == 1
        assert data['results'][0]['caption'] == "post with tag2"

        # Test searching for non-existent tag
        res = client.get(f"{url}?tag=nonexistenttag")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data['count'] == 0

    def test_list_posts_with_both_tag_and_keyword(self, client, user1, tag1):
        """GET /api/posts/?tag=...&keyword=... - 태그와 키워드 모두 제공 시 태그 우선 적용을 테스트합니다."""
        # Create posts with different tags and captions
        from snapsapi.apps.posts.models import Post, PostImage, Tag

        # Create a new tag for testing
        tag2 = Tag.objects.create(name="pythontag", is_featured=True)

        # Post with tag1 and "hello" in caption
        post1 = Post.objects.create(
            user=user1,
            caption="hello world post with tag1",
            is_deleted=False,
            is_active=True,
        )
        post1.tags.add(tag1)
        PostImage.objects.create(
            post=post1,
            url="https://example.com/image1.png",
            order=0
        )

        # Post with tag2 and "hello" in caption
        post2 = Post.objects.create(
            user=user1,
            caption="hello world post with tag2",
            is_deleted=False,
            is_active=True,
        )
        post2.tags.add(tag2)
        PostImage.objects.create(
            post=post2,
            url="https://example.com/image2.png",
            order=0
        )

        # Test searching with both tag and keyword
        # Should prioritize tag and ignore keyword
        url = reverse('posts:posts-list-create')
        res = client.get(f"{url}?tag={tag1.name}&keyword=hello")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data['count'] == 1
        assert data['results'][0]['caption'] == "hello world post with tag1"

        # Test with different tag but same keyword
        res = client.get(f"{url}?tag={tag2.name}&keyword=hello")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data['count'] == 1
        assert data['results'][0]['caption'] == "hello world post with tag2"

    def test_create_posts_should_return_201_created(self, jwt_client):
        """POST /api/posts/ - 인증된 사용자의 게시물 생성을 테스트합니다."""
        url = reverse('posts:posts-list-create')
        payload = CREATE_POST_PAYLOAD
        res = jwt_client.post(url, payload, format='json')
        data = res.json()

        assert res.status_code == status.HTTP_201_CREATED
        assert 'metadata' in data
        assert data['caption'] == payload['caption']
        assert data['images'] == UPDATED_POST_PAYLOAD['images']
        assert data['tags'] == payload['tags']

    def test_create_posts_should_return_401_unauthorized(self, client):
        """POST /api/posts/ - 비인증 사용자의 게시물 생성 실패를 테스트합니다."""
        url = reverse('posts:posts-list-create')
        payload = CREATE_POST_PAYLOAD
        res = client.post(url, payload, format='json')
        assert res.status_code == status.HTTP_401_UNAUTHORIZED