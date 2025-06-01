from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from snapsapi.apps.users.views import (
    SocialRegisterView,
    GoogleConnectView,
)

app_name = 'users'

urlpatterns = []

urlpatterns += [
    path('social-register/', SocialRegisterView.as_view(), name='social_register'),
    # path('social-registerrr/', GoogleConnectView.as_view(), name='social_register'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
