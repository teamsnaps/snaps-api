from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from snapsapi.apps.users.views import (
    SocialRegisterView,
)

app_name = 'users'

urlpatterns = []

urlpatterns += [
    path('social-register/', SocialRegisterView.as_view(), name='social-register'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
