from django.urls import path, include
from snapsapi.apps.comments import views
from snapsapi.apps.likes.views import CommentLikeToggleView

app_name = 'comments'

urlpatterns = []

urlpatterns += [
    # path('', views.CommentListCreateView.as_view(), name='posts-list-create'),
    path('<uuid:uid>/', views.CommentDetailView.as_view(), name='posts-detail'),
    path('<uuid:uid>/likes/', CommentLikeToggleView.as_view(), name='comment-like-toggle'),
]
