from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from snapsapi.apps.posts import views

app_name = 'posts'

urlpatterns = []

urlpatterns += [
    path('', views.PostCreateView.as_view(), name='posts-list-create'),
    path('<str:uid>/', views.PostUpdateView.as_view(), name='posts-update'),
    path('del/<str:uid>/', views.PostDeleteView.as_view(), name='posts-delete'),
    path('media/presigned-url/', views.PresignedURLView.as_view(), name='posts-media-presigned-url'),
    # path('feed_mock/', views.FeedMockListView.as_view(), name='feed_mock'),
    # path('feed/', views.FeedMockListView.as_view(), name='feed_mock'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
