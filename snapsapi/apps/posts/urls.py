from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from snapsapi.apps.posts import views

app_name = 'posts'

urlpatterns = []

urlpatterns += [
    path('', views.PostListCreateView.as_view(), name='posts-list-create'),
    path('<uuid:uid>/', views.PostDetailView.as_view(), name='posts-detail'),
    path('presigned-url/', views.PresignedURLView.as_view(), name='posts-presigned-url'),
    path('feed_mock/', views.FeedMockListView.as_view(), name='feed_mock'),
    path('feed/', views.FeedMockListView.as_view(), name='feed_mock'),
    # path('feed2/', views.PostListSerializer.as_view(), name='feed_mock'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
