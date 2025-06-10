from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from snapsapi.apps.core import views

app_name = 'core'

urlpatterns = []

urlpatterns += [
    path('story/', views.StoryListCreateView.as_view(), name='story'),
    path('posts/', views.PostListCreateView.as_view(), name='posts'),
    path('posts/<str:uid>/', views.PostDetailView.as_view(), name='posts_update'),
    path('posts/delete/<str:uid>/', views.PostSoftDeleteView.as_view(), name='posts_delete'),
    path('feed_mock/', views.FeedMockListView.as_view(), name='feed_mock'),
    path('feed/', views.FeedMockListView.as_view(), name='feed_mock'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
