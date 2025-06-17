from django.urls import path
from snapsapi.apps.core.views import home, health_check

urlpatterns = [
    # 루트 URL
    # path('', home, name='home'),
    # 헬스체크 URL
    path('health/', health_check, name='health_check'),
]
