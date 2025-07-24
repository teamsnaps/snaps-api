# tests/apps/notifications/test_fcm.py
import pytest
from unittest.mock import patch, MagicMock
from snapsapi.apps.notifications.services import FCMService
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestFCMService:
    @patch('firebase_admin.messaging.send')
    def test_send_notification(self, mock_send, fcm_device):
        # 모킹된 함수 설정
        mock_send.return_value = "message_id_123"

        # 서비스 호출
        fcm_service = FCMService()
        result = fcm_service.send_notification(
            token=fcm_device.registration_id,
            title="테스트 제목",
            body="테스트 내용",
            data={"key": "value"}
        )

        # 검증
        mock_send.assert_called_once()
        assert result == "message_id_123"

    @patch('snapsapi.apps.notifications.services.messaging.send_multicast')
    def test_send_multicast_notification(self, mock_send_multicast, user, fcm_device):
        # 모킹된 함수 설정
        mock_response = MagicMock()
        mock_response.success_count = 1
        mock_response.failure_count = 0
        mock_send_multicast.return_value = mock_response

        # 서비스 호출
        fcm_service = FCMService()
        result = fcm_service.send_notifications_to_user(
            user_id=user.id,
            title="테스트 다중 전송",
            body="테스트 내용"
        )

        # 검증
        mock_send_multicast.assert_called_once()
        assert result.success_count == 1
        assert result.failure_count == 0

    @patch('firebase_admin.messaging.send')
    def test_notification_failure(self, mock_send, fcm_device):
        # 오류 발생 시뮬레이션
        mock_send.side_effect = Exception("FCM 서버 오류")

        # 서비스 호출 및 예외 확인
        fcm_service = FCMService()
        with pytest.raises(Exception):
            fcm_service.send_notification(
                token="invalid_token",
                title="실패 테스트",
                body="오류 발생 예상"
            )