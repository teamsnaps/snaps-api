from rest_framework import status
from drf_spectacular.utils import OpenApiExample

POST_CREATE_REQUEST_EXAMPLE = [
    OpenApiExample(
        "성공 예시",
        value={
            "images": [
                {
                    "url": "https://example.com/path/to/post/image1.jpg"
                },
                {
                    "url": "https://example.com/path/to/post/image2.jpg"
                }
            ],
            "caption": "Enjoying a beautiful day out! Here are some great photos.",
            "tags": [
                "nature",
                "photography",
                "travel"
            ]
        },
        status_codes=[str(status.HTTP_201_CREATED)],
    )
]

POST_CREATE_RESPONSE_EXAMPLE = [
    OpenApiExample(
        "성공 예시",
        value={
            "metadata": {
                "post_uid": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "user_uid": "f0e9d8c7-b6a5-4321-fedc-ba9876543210"
            },
            "user": {
                "uid": "f0e9d8c7-b6a5-4321-fedc-ba9876543210",
                "username": "sample_user",
                "image": "https://example.com/path/to/profile_image.jpg",
                "bio": "This is a sample bio description for a user profile.",
                "is_me": False,
                "is_following": True
            },
            "images": [
                {
                    "url": "https://example.com/path/to/post/image1.jpg"
                },
                {
                    "url": "https://example.com/path/to/post/image2.jpg"
                }
            ],
            "caption": "Enjoying a beautiful day out! Here are some great photos.",
            "tags": [
                "nature",
                "photography",
                "travel"
            ],
            "likes_count": 12853,
            "comments_count": 312,
            "is_liked": False,
            "is_public": True,
            "created_at": "2025-06-15T10:30:00Z",
            "updated_at": "2025-06-15T10:35:00Z"
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
