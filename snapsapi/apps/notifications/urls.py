from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from snapsapi.apps.notifications.views import register_device

app_name = 'notifications'

urlpatterns = []

urlpatterns += [
    path('devices/', register_device, name='register-device'),
]