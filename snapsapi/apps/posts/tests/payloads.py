CREATE_POST_PAYLOAD = {
    "caption": "test caption",
    "images": [
        {
            "url": "uploads/2025/06/11/photo1.jpg"
        },
        {
            "url": "uploads/2025/06/11/photo2.jpg"
        }
    ],
    "tags": ["new tag"],
    # "mentions": ["@mina", "@jinho"],           # 유저 태그
    # "location": "강릉 경포대",                # 위치 태그
    # "visibility": "public",                  # or "friends", "private"
    # "allow_comments": True                   # 댓글 허용 여부
}

UPDATED_POST_PAYLOAD = {
    "caption": "test caption",
    "images": [
        {
            "url": "/uploads/2025/06/11/photo1.jpg"
        },
        {
            "url": "/uploads/2025/06/11/photo2.jpg"
        }
    ],
    "tags": ["new tag"],
    # "mentions": ["@mina", "@jinho"],           # 유저 태그
    # "location": "강릉 경포대",                # 위치 태그
    # "visibility": "public",                  # or "friends", "private"
    # "allow_comments": True                   # 댓글 허용 여부
}
