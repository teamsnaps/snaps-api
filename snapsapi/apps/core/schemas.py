from drf_spectacular.utils import OpenApiExample
from rest_framework import status

# ✅ Request Body Example
MOCK_PRIVATE_FEED = [
    {
        "metadata": {
            "post_uid": "kYX36S...",
            "user_uid": "QiRSZt..."
        },
        "profile": {
            "username": "panibottle",
            "image": "https://mybucket.s3.amazonaws.com/..."
        },
        "images": [
            {
                "url": "/test_image/private_feed_image/IMG_1408.JPG"
            },
            {
                "url": "/test_image/private_feed_image/IMG_1550.jpeg"
            },
            {
                "url": "/test_image/private_feed_image/IMG_1441.jpeg"
            },
            {
                "url": "/test_image/private_feed_image/IMG_1896.jpeg"
            },
            {
                "url": "/test_image/private_feed_image/IMG_2209.JPG"
            },
            {
                "url": "/test_image/private_feed_image/IMG_2211.JPG"
            }
        ],
        "context": {
            "username": "panibottle",
            "caption": "MOCK_PRIVATE_FEED",
            "tags": ["여행", "일본여행", "오사카", "교토"]
        },
        "created_at": "2024-06-02T09:16:21.654Z",
        "updated_at": "2024-06-11T07:23:29.139Z",
        "likes_count": 0,
        "comments_count": 0
    }
]

MOCK_PUBLIC_FEED = [
    {
        "metadata": {
            "post_uid": "kYX36S...",
            "user_uid": "QiRSZt..."
        },
        "profile": {
            "username": "panibottle",
            "image": "https://mybucket.s3.amazonaws.com/..."
        },
        "images": [
            {
                "url": "/test_image/public_feed_image/IMG_0258.jpeg"
            },
            {
                "url": "/test_image/public_feed_image/IMG_0265.jpeg"
            },
            {
                "url": "/test_image/public_feed_image/IMG_0270.jpeg"
            },
            {
                "url": "/test_image/public_feed_image/IMG_0272.jpeg"
            },
            {
                "url": "/test_image/public_feed_image/IMG_0281.jpeg"
            },
            {
                "url": "/test_image/public_feed_image/IMG_5425.jpeg"
            },
        ],
        "context": {
            "username": "panibottle",
            "caption": "MOCK_PUBLIC_FEED",
            "tags": ["여행", "일본여행", "오사카", "교토"]
        },
        "created_at": "2024-06-02T09:16:21.654Z",
        "updated_at": "2024-06-11T07:23:29.139Z",
        "likes_count": 0,
        "comments_count": 0
    }
]
