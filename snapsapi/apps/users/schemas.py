from drf_spectacular.utils import OpenApiExample

USER_REGISTRATION_RESPONSE_EXAMPLE = [
    OpenApiExample(
        "회원가입 응답 예시",
        summary="User Registration Response Example",
        description="회원가입 응답 예시입니다.",
        value={
            "access": "eyJhbGciOiJIU...k5N0xXvYeVC4",
            "refresh": "eyJ0b2tl0eXBl...CI6MTc0OTUwM",
            "user": {
                "pk": 7,
                "username": "User_a090j_RX",
                "email": "ask4git@gmail.com",
                "first_name": "진혁",
                "last_name": "최"
            }
        },
        response_only=True,
    )
]
