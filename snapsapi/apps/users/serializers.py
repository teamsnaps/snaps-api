from rest_framework import serializers
from dj_rest_auth.registration.serializers import SocialLoginSerializer


class SocialLoginWriteSerializer(SocialLoginSerializer):
    access_token = serializers.CharField()
    provider = serializers.ChoiceField(choices=['google', 'kakao', 'naver'])


class SocialLoginReadSerializer(SocialLoginSerializer):
    provider = serializers.ChoiceField(choices=['google', 'kakao', 'naver'])
