from rest_framework import serializers


class LikeResponseSerializer(serializers.Serializer):
    likes_count = serializers.IntegerField(help_text="Updated number of likes")
    is_liked = serializers.BooleanField(help_text="Whether the current user has liked it")
