import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .payloads import CREATE_POST_PAYLOAD


@pytest.fixture
def jwt_client(api_client, user1):
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


@pytest.mark.django_db
class TestPosts:
    def test_create_posts_should_return_201_created(self, jwt_client):
        create_url = reverse('core:posts-list-create')
        payload = CREATE_POST_PAYLOAD
        res = jwt_client.post(create_url, payload, format='json')
        data = res.json()

        assert res.status_code == status.HTTP_201_CREATED
        assert 'uid' in data
        assert data['caption'] == payload['caption']
        assert data['images'] == payload['images']
        assert data['tags_names'] == payload['tags']
        # assert data['user'] == user1.id

    def test_create_posts_should_return_401_unauthorized(self, invalid_jwt_client, user1):
        create_url = reverse('core:posts-list-create')
        payload = CREATE_POST_PAYLOAD
        res = invalid_jwt_client.post(create_url, payload, format='json')

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


    # def test_list_posts_should_return_200_ok(self, jwt_client):






    # def test_soft_delete_posts_should_return_200_and_set_is_deleted_flag(self, jwt_client):
    #     # 1) 게시글 생성
    #     create_url = reverse('core:posts-list-create')
    #     res1 = jwt_client.post(create_url, CREATE_POST_PAYLOAD, format='json')
    #     uid = res1.json()['uid']
    #
    #     # 2) soft-delete 엔드포인트 호출
    #     delete_url = reverse('core:posts-delete', kwargs={'uid': uid})
    #     res2 = jwt_client.patch(delete_url)
    #     assert res2.status_code == status.HTTP_200_OK
    #     assert res2.json()['detail'] == 'soft deleted'
    #
    #     # 3) 실제 필드 값 확인
    #     detail_url = reverse('core:posts_update', kwargs={'uid': uid})
    #     res3 = jwt_client.get(detail_url)
    #     assert res3.status_code == status.HTTP_200_OK
    #     assert res3.json()['is_deleted'] is True
    #
    # def test_update_posts_should_toggle_is_active_flag(self, jwt_client):
    #     # 1) 게시글 생성
    #     create_url = reverse('core:post-list-create')
    #     res1 = jwt_client.post(create_url, CREATE_POST_PAYLOAD, format='json')
    #     uid = res1.json()['uid']
    #
    #     # 2) is_active=False 로 숨기기
    #     detail_url = reverse('core:posts_update', kwargs={'uid': uid})
    #     res2 = jwt_client.patch(detail_url, {'is_active': False}, format='json')
    #     assert res2.status_code == status.HTTP_200_OK
    #     assert res2.json()['is_active'] is False
    #
    #     # 3) is_active=True 로 다시 보이기
    #     res3 = jwt_client.patch(detail_url, {'is_active': True}, format='json')
    #     assert res3.status_code == status.HTTP_200_OK
    #     assert res3.json()['is_active'] is True
