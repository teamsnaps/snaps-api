from drf_spectacular.utils import OpenApiExample
from rest_framework import status

# ✅ Request Body Example
SOCIAL_LOGIN_REQUEST_EXAMPLE = [
    OpenApiExample(
        "소셜 로그인 요청 예시",
        description="소셜 로그인 요청 예시입니다.",
        value={
            "access_token": "ya29.a0ARrdaM...abc123",
            "provider": "google"
        },
        request_only=True
    )
]

# ✅ Response Body Example (201 CREATED)
USER_REGISTRATION_RESPONSE_EXAMPLE = [
    OpenApiExample(
        "회원가입 응답 예시",
        summary="User Registration Response Example",
        description="회원가입 응답 예시입니다.",
        value={
            "access": "ya29.a0ARrdaM...abc123",
            "refresh": "ya29.a0ARrdaM...abc123",
            "user": {
                "uid": "PzxwwwOnV",
                "username": "User_a090j_RX",
                "email": "ask4git@gmail.com",
                "first_name": "진혁",
                "last_name": "최"
            }
        },
        response_only=True,
    )
]

USER_REGISTRATION_RESPONSE_ERROR_EXAMPLE = [
    OpenApiExample(
        "회원가입 에러 응답 예시",
        summary="User Registration Response Example",
        description="회원가입 에러 응답 예시입니다.",
        value={
            "detail": "OAuth2 인증에 실패했습니다. 유효한 access_token을 제공해주세요."
        },
        response_only=True,
    )
]
