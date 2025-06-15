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

POST_CREATE_REQUEST_EXAMPLE = [
    OpenApiExample(
        "성공 예시",
        value={
            "caption": "여러장 사진 업로드!",
            "images": [
                "https://.../image1.jpg",
                "https://.../image2.jpg"
            ],
            "tags": ["바다", "여행", "산책"]
        },
        status_codes=[str(status.HTTP_201_CREATED)],
    )
]
POST_CREATE_RESPONSE_EXAMPLE = [
    OpenApiExample(
        "성공 예시",
        value={
            "uid": "d0e914a4-3b3c-413a-a994-efb540a3c871",
            "caption": "여러장 사진 업로드!",
            "images": [
                "https://.../image1.jpg",
                "https://.../image2.jpg"
            ],
            "tags": ["바다", "여행", "산책"]
        },
        status_codes=[str(status.HTTP_201_CREATED)],
    )
]

PRESIGNED_POST_URL_REQUEST_EXAMPLE = [
    OpenApiExample(
        "호출 예시",
        value={
            "files": [
                {
                    "file_name": "cat.jpg",
                    "file_type": "image/jpeg"
                },
                {
                    "file_name": "dog.png",
                    "file_type": "image/png"
                }
            ]
        }
    )
]
PRESIGNED_POST_URL_RESPONSE_EXAMPLE = [
    OpenApiExample(
        "성공 예시",
        value={
            "results": [
                {
                    "file_name": "cat.jpg",
                    "presigned_url": {
                        "url": "https://snapsapi-app-media.s3.amazonaws.com/",
                        "fields": {
                            "key": "posts/user_CT2SZym4cXuvZXZCbiTKMf/2025/06/12/29e7d3bc-abfa-48b0-b636-da570c88ebf8.jpg",
                            "x-amz-algorithm": "AWS4-HMAC-SHA256",
                            "x-amz-credential": "AKIAVSLUWUIGOPPODMW4/20250612/ap-northeast-2/s3/aws4_request",
                            "x-amz-date": "20250612T122453Z",
                            "policy": "eyJleHBpcmF0aW9uIjog...YxMlQxMjI0NTNaIn1dfQ==",
                            "x-amz-signature": "86d689f1d10099f3579954f9a7d2006a286993389e6b7fb4ea6a6a798c6bdf5b"
                        }
                    }
                },
                {
                    "file_name": "dog.png",
                    "presigned_url": {
                        "url": "https://snapsapi-app-media.s3.amazonaws.com/",
                        "fields": {
                            "key": "posts/user_CT2SZym4cXuvZXZCbiTKMf/2025/06/12/92201323-91df-4caf-b2d5-8d360b9b7d87.png",
                            "x-amz-algorithm": "AWS4-HMAC-SHA256",
                            "x-amz-credential": "AKIAVSLUWUIGOPPODMW4/20250612/ap-northeast-2/s3/aws4_request",
                            "x-amz-date": "20250612T122453Z",
                            "policy": "eyJleHBpcmF0aW9uIjog...YxMlQxMjI0NTNaIn1dfQ==",
                            "x-amz-signature": "316aa73e77287973391959024bc6cb9b1fbb2df77e6a81650569ad7c065e599c"
                        }
                    }
                }
            ]
        }
        ,
        status_codes=[str(status.HTTP_200_OK)],
    )
]
