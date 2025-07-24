# tests/apps/notifications/test_api.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from snapsapi.apps.notifications.models import FCMDevice

@pytest.mark.django_db
class TestFCMAPI:
    @pytest.fixture
    def api_client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_device_registration(self, api_client, user):
        # 디바이스 등록 요청
        register_url = reverse('notifications:fcm-device-register')
        data = {
            'registration_id': 'test_token_456',
            'type': 'android'
        }
        response = api_client.post(register_url, data, format='json')

        # 응답 확인
        assert response.status_code == 201

        # 디바이스가 저장되었는지 확인
        device_exists = FCMDevice.objects.filter(
            user=user,
            registration_id=data['registration_id']
        ).exists()
        assert device_exists is True

    def test_duplicate_device_registration(self, api_client, user):
        # 기존 디바이스 생성
        FCMDevice.objects.create(
            user=user,
            registration_id='existing_token',
            type='web'
        )

        # 같은 토큰으로 다시 등록 요청
        register_url = reverse('notifications:fcm-device-register')
        data = {
            'registration_id': 'existing_token',
            'type': 'android'  # 타입 변경
        }
        response = api_client.post(register_url, data, format='json')

        # 업데이트 성공 확인
        assert response.status_code == 200

        # 디바이스 타입이 업데이트되었는지 확인
        device = FCMDevice.objects.get(registration_id='existing_token')
        assert device.type == 'android'