from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from snapsapi.apps.posts import views
from snapsapi.apps.comments.views import CommentListCreateView
from snapsapi.apps.likes.views import PostLikeToggleView

app_name = 'posts'

urlpatterns = []

urlpatterns += [
    path('', views.PostListCreateView.as_view(), name='posts-list-create'),
    path('<uuid:uid>/', views.PostDetailView.as_view(), name='posts-detail'),
    path('<uuid:uid>/comments/', CommentListCreateView.as_view(), name='comments-list-create'),
    path('<uuid:uid>/likes/', PostLikeToggleView.as_view(), name='like-toggle'),
    path('presigned-url/', views.PostImageUploadURLView.as_view(), name='posts-presigned-url'),
    path('tags/', views.TagListView.as_view(), name='tags-list'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
