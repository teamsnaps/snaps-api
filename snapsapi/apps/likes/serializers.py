from rest_framework import serializers


class LikeResponseSerializer(serializers.Serializer):
    """
    좋아요 액션 후의 응답을 위한 Serializer입니다.
    """
    likes_count = serializers.IntegerField(help_text="업데이트된 좋아요 개수")
    is_liked = serializers.BooleanField(help_text="현재 사용자의 좋아요 여부")
