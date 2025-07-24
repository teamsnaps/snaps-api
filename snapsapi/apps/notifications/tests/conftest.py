# tests/conftest.py
import pytest
from django.contrib.auth import get_user_model
from snapsapi.apps.notifications.models import FCMDevice

User = get_user_model()

@pytest.fixture
def user():
    """테스트용 사용자 생성"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword'
    )

@pytest.fixture
def fcm_device(user):
    """테스트용 FCM 디바이스 생성"""
    return FCMDevice.objects.create(
        user=user,
        registration_id='test_token_123',
        type='web',
        active=True
    )