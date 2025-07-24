# tests/apps/notifications/test_models.py
import pytest
from django.db.utils import IntegrityError
from snapsapi.apps.notifications.models import FCMDevice

@pytest.mark.django_db
class TestFCMDeviceModel:
    def test_create_device(self, user):
        device = FCMDevice.objects.create(
            user=user,
            registration_id='test_token_123',
            type='web'
        )

        assert device.user == user
        assert device.registration_id == 'test_token_123'
        assert device.type == 'web'
        assert device.active is True

    def test_unique_constraint(self, user):
        # 첫 번째 디바이스 생성
        FCMDevice.objects.create(
            user=user,
            registration_id='same_token',
            type='web'
        )

        # 같은 사용자와 토큰으로 두 번째 디바이스 생성 시도
        with pytest.raises(IntegrityError):
            FCMDevice.objects.create(
                user=user,
                registration_id='same_token',
                type='android'
            )

    def test_str_representation(self, user):
        device = FCMDevice.objects.create(
            user=user,
            registration_id='test_token_456',
            type='ios'
        )

        expected_str = f"{user.username}'s ios device"
        assert str(device) == expected_str