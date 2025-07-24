# notifications/services.py
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from snapsapi.apps.notifications.models import FCMDevice


class FCMService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FCMService, cls).__new__(cls)
            # Firebase Admin SDK 초기화
            try:
                # 보호된 멤버에 접근하지 않고 default app이 있는지 확인
                try:
                    firebase_admin.get_app()
                except ValueError:
                    # 앱이 초기화되지 않았으면 ValueError 발생
                    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
                    firebase_admin.initialize_app(cred)
            except Exception as e:
                print(f"Firebase 초기화 실패: {e}")
        return cls._instance

    def send_notifications_to_user(self, user_id, title, body, data=None):
        """특정 사용자의 모든 활성 디바이스에 알림을 한번에 전송 (효율적인 방식)"""
        devices = FCMDevice.objects.filter(user_id=user_id, active=True)
        tokens = [device.registration_id for device in devices]

        if not tokens:
            return None  # 보낼 기기가 없으면 종료

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=tokens,
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    icon='/assets/icons/icon-192x192.png',
                ),
                fcm_options=messaging.WebpushFCMOptions(
                    link=data.get('url', '/') if data else '/'
                )
            )
        )

        # send_multicast를 사용하여 한번에 모든 토큰에 발송
        batch_response = messaging.send_multicast(message)

        # 실패한 토큰이 있는 경우, 해당 디바이스를 비활성화
        if batch_response.failure_count > 0:
            failed_tokens = []
            for idx, response in enumerate(batch_response.responses):
                if not response.success:
                    # 응답 순서는 토큰 리스트 순서와 일치합니다.
                    failed_tokens.append(tokens[idx])

            if failed_tokens:
                FCMDevice.objects.filter(registration_id__in=failed_tokens).update(active=False)

        return batch_response

    def send_notification(self, token, title, body, data=None):
        """단일 기기에 알림 전송"""
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    icon='/assets/icons/icon-192x192.png',
                ),
                fcm_options=messaging.WebpushFCMOptions(
                    link=data.get('url', '/') if data else '/'
                )
            )
        )

        return messaging.send(message)
