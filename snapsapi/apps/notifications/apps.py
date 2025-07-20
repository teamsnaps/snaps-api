# notifications/apps.py
from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials
from django.conf import settings

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'snapsapi.apps.notifications'

    def ready(self):
        # 앱이 준비될 때 Firebase 초기화
        if settings.FIREBASE_CONFIG_VALID:
            try:
                # 보호된 멤버에 접근하지 않는 방식으로 변경
                try:
                    firebase_admin.get_app()
                    print("Firebase 이미 초기화됨")
                except ValueError:
                    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
                    firebase_admin.initialize_app(cred)
                    print("Firebase 초기화 성공")
            except Exception as e:
                print(f"Firebase 초기화 실패: {e}")
        else:
            print("Firebase 설정이 완전하지 않아 초기화를 건너뜁니다.")