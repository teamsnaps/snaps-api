from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from snapsapi.apps.users.views import (
    SocialLoginView,
    GoogleConnectView,
)

app_name = 'users'

urlpatterns = []

urlpatterns += [
    path('social-login/', SocialLoginView.as_view(), name='social_login'),
    # path('social-registerrr/', GoogleConnectView.as_view(), name='social_register'),
]

