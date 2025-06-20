from rest_framework import serializers
from dj_rest_auth.registration.serializers import SocialLoginSerializer


class SocialLoginWriteSerializer(SocialLoginSerializer):
    access_token = serializers.CharField()
    provider = serializers.ChoiceField(choices=['google', 'kakao', 'naver'])


class SocialLoginReadSerializer(SocialLoginSerializer):
    provider = serializers.ChoiceField(choices=['google', 'kakao', 'naver'])


class UserSerializer(serializers.Serializer):
    uid = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

class SocialLoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()

class FollowResponseSerializer(serializers.Serializer):
    """
    팔로우/언팔로우 액션 후의 응답을 위한 Serializer입니다.
    """
    is_following = serializers.BooleanField(help_text="현재 사용자의 팔로우 여부")
    followers_count = serializers.IntegerField(help_text="대상 유저의 팔로워 수")
    following_count = serializers.IntegerField(help_text="대상 유저의 팔로잉 수")
