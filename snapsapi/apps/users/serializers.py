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