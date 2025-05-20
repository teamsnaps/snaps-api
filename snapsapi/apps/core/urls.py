from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from snapsapi.apps.core import views


urlpatterns = []

urlpatterns += [
    path('story/', views.StoryListCreateView.as_view(), name='story'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

app_name = 'core'