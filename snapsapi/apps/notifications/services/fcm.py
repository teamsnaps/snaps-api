import logging

import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from urllib.parse import urljoin

from snapsapi.apps.notifications.models import FCMDevice

# 로거 인스턴스 생성
logger = logging.getLogger(__name__)


class FCMService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FCMService, cls).__new__(cls)
            try:
                firebase_admin.get_app()
            except ValueError:
                logger.error("Firebase App이 초기화되지 않았습니다. apps.py 설정을 확인하세요.")
                if settings.FIREBASE_CONFIG_VALID:
                    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
                    firebase_admin.initialize_app(cred)
                    logger.info("FCMService에서 비상 Firebase 초기화를 수행했습니다.")
                else:
                    logger.error("Firebase 설정이 유효하지 않아 초기화할 수 없습니다.")

        return cls._instance

    def send_notifications_to_user(self, user_id, title, body, data=None):
        """특정 사용자의 모든 활성 디바이스에 알림을 한번에 전송"""
        logger.info(f"FCM: user_id '{user_id}'에 대한 알림 전송을 시작합니다.")
        devices = FCMDevice.objects.filter(user_id=user_id, active=True)
        tokens = [device.registration_id for device in devices]

        if not tokens:
            logger.warning(f"FCM: user_id '{user_id}'에 대한 활성 기기가 없어 알림을 보내지 않았습니다.")
            return None

        logger.info(f"FCM: user_id '{user_id}'에게 {len(tokens)}개의 토큰으로 알림 전송을 시도합니다.")

        relative_url = data.get('url', '/') if data else '/'
        full_url = urljoin(settings.BASE_FRONTEND_URL, relative_url)
        icon_url = urljoin(settings.BASE_FRONTEND_URL, '/assets/icons/icon-192x192.png')

        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            tokens=tokens,
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(icon=icon_url),
                fcm_options=messaging.WebpushFCMOptions(link=full_url)
            )
        )

        try:
            # send_multicast 대신 send_each_for_multicast 사용
            batch_response = messaging.send_each_for_multicast(message)
            logger.info(f"FCM 전송 결과: 성공 {batch_response.success_count}개, 실패 {batch_response.failure_count}개")

            if batch_response.failure_count > 0:
                failed_tokens = []
                for idx, response in enumerate(batch_response.responses):
                    if not response.success:
                        failed_token = tokens[idx]
                        failed_tokens.append(failed_token)
                        logger.error(f"FCM 전송 실패: 토큰 '{failed_token}', 에러: {response.exception}")
                if failed_tokens:
                    FCMDevice.objects.filter(registration_id__in=failed_tokens).update(active=False)
                    logger.warning(f"{len(failed_tokens)}개의 만료된 FCM 토큰을 비활성화 처리했습니다.")
            return batch_response
        except Exception as e:
            logger.error(f"FCM 알림 전송 중 예외 발생: {e}", exc_info=True)
            return None

    def send_notification(self, token, title, body, data=None):
        """단일 기기에 알림 전송"""
        relative_url = data.get('url', '/') if data else '/'
        # BASE_BACKEND_URL과 상대 경로를 조합하여 전체 URL 생성
        full_url = urljoin(settings.BASE_FRONTEND_URL, relative_url)

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
                    # link=full_url
                    link='https://snaps-front.vercel.app/feed',
                )
            )
        )

        return messaging.send(message)
