from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from snapsapi.apps.users.views import (
    SocialLoginView,
    GoogleConnectView, FollowToggleView, UserProfileView
)

app_name = 'users'

urlpatterns = []

urlpatterns += [
    path('social-login/', SocialLoginView.as_view(), name='social_login'),
    path('<str:user_uid>/', UserProfileView.as_view(), name='social_login'),
    # path('social-registerrr/', GoogleConnectView.as_view(), name='social_register'),
    path('<str:user_uid>/follow/', FollowToggleView.as_view(), name='user-follow-toggle'),

]

# res = [
#     {
#         "metadata": {
#             "post_uid": "83cf8302-eb63-434c-bc5d-e3e25afd7536",
#             "user_uid": "MiCP89GwdGTXCrAM3yqtCD"
#         },
#         "profile": {
#             "username": "User_Wq4HHN",
#             "image": null
#         },
#         "images": [
#             {
#
#                 "url": "https://mybucket.s3.ap-northeast-2.amazonaws.com/uploads/2025/06/11/photo1_acsndiouacheof.jpg"
#             },
#             {
#                 "url": "https://mybucket.s3.ap-northeast-2.amazonaws.com/uploads/2025/06/11/photo1_skadjchiewufsa.jpg"
#             }
#         ],
#         "context": {
#             "username": "User_Wq4HHN",
#             "caption": "여러장 사진 업로드!",
#             "tags": [
#                 "바다",
#                 "여행",
#                 "산책"
#             ]
#         },
#         "created_at": "2025-06-18T14:51:46.759511Z",
#         "updated_at": "2025-06-18T14:51:46.759530Z",
#         "likes_count": 0,
#         "comments_count": 0
#     }
# ]
