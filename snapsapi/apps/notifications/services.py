# notifications/services.py
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from snapsapi.apps.notifications.models import FCMDevice


# Todo: register_device api 추가해야함

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

    def send_to_user(self, user_id, title, body, data=None):
        """특정 사용자의 모든 디바이스에 알림 전송"""
        devices = FCMDevice.objects.filter(user_id=user_id, active=True)

        if not devices.exists():
            return {'success': False, 'message': 'No active devices found for user'}

        results = []
        for device in devices:
            try:
                result = self.send_notification(
                    token=device.registration_id,
                    title=title,
                    body=body,
                    data=data
                )
                results.append({'device_id': device.id, 'success': True, 'message_id': result})
            except Exception as e:
                # 토큰이 유효하지 않은 경우 디바이스 비활성화
                if 'invalid-registration-token' in str(e) or 'registration-token-not-registered' in str(e):
                    device.active = False
                    device.save()

                results.append({'device_id': device.id, 'success': False, 'error': str(e)})

        return {'success': True, 'results': results}


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
