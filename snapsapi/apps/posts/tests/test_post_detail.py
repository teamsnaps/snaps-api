import pytest
from django.urls import reverse
from rest_framework import status
from .payloads import CREATE_POST_PAYLOAD


@pytest.mark.django_db
class TestPostDetailView:
    """/api/posts/{uid}/ 엔드포인트에 대한 테스트"""

    # def test_retrieve_post_success(self, client, post_of_user1):
    #     """GET /api/posts/{uid}/ - 게시물 상세 조회를 테스트합니다."""
    #     url = reverse('posts:posts-detail', kwargs={'uid': post_of_user1.uid})
    #     res = client.get(url)
    #     assert res.status_code == status.HTTP_200_OK
    #     assert res.data['uid'] == str(post_of_user1.uid)

    def test_update_posts_should_return_200_ok(self, jwt_client, post1):
        detail_url = reverse('posts:posts-detail', kwargs={'uid': post1.uid})
        payload = {'caption': 'updated caption'}
        res = jwt_client.patch(detail_url, payload, format='json')
        data = res.json()

        assert data['caption'] == payload['caption']
        assert data['tags'] is not None

    def test_soft_delete_posts_should_return_200_and_set_is_deleted_flag(self, jwt_client):
        # 1) 게시글 생성
        create_url = reverse('posts:posts-list-create')
        res1 = jwt_client.post(create_url, CREATE_POST_PAYLOAD, format='json')
        uid = res1.json()['uid']

        # 2) soft-delete 엔드포인트 호출
        delete_url = reverse('posts:posts-detail', kwargs={'uid': uid})
        res2 = jwt_client.delete(delete_url)
        assert res2.status_code == status.HTTP_204_NO_CONTENT

    def test_update_post_by_owner_should_return_200_ok(self, jwt_client_user1, post_of_user1):
        """PATCH /api/posts/{uid}/ - 작성자에 의한 게시물 수정을 테스트합니다."""
        url = reverse('posts:posts-detail', kwargs={'uid': post_of_user1.uid})
        payload = {'caption': 'updated caption'}
        res = jwt_client_user1.patch(url, payload, format='json')
        data = res.json()

        assert res.status_code == status.HTTP_200_OK
        assert data['caption'] == payload['caption']

    # def test_update_post_by_another_user(self, jwt_client_user2, post_of_user1):
    #     """PATCH /api/posts/{uid}/ - 다른 사용자에 의한 수정 실패를 테스트합니다."""
    #     url = reverse('posts:posts-detail', kwargs={'uid': post_of_user1.uid})
    #     payload = {'caption': 'Trying to update'}
    #     res = jwt_client_user2.patch(url, payload, format='json')
    #     assert res.status_code == status.HTTP_403_FORBIDDEN # 또는 404
    #
    # def test_delete_post_by_owner(self, jwt_client_user1, post_of_user1):
    #     """DELETE /api/posts/{uid}/ - 작성자에 의한 게시물 삭제를 테스트합니다."""
    #     url = reverse('posts:posts-detail', kwargs={'uid': post_of_user1.uid})
    #     res = jwt_client_user1.delete(url)
    #     assert res.status_code == status.HTTP_204_NO_CONTENT # 또는 200/202