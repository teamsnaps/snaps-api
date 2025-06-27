from django.contrib.auth import get_user_model
from rest_framework import serializers
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from datetime import timezone, datetime, UTC, timedelta

from snapsapi.apps.posts.models import Post
from snapsapi.apps.users.models import Profile
from snapsapi.apps.core.models import Follow


class SocialLoginWriteSerializer(SocialLoginSerializer):
    access_token = serializers.CharField()
    provider = serializers.ChoiceField(choices=['google', 'kakao', 'naver'])


class SocialLoginReadSerializer(SocialLoginSerializer):
    provider = serializers.ChoiceField(choices=['google', 'kakao', 'naver'])


class UserLoginSerializer(serializers.Serializer):
    uid = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()





class UserProfileSerializer(serializers.Serializer):
    """
    User profile information for display purposes.
    Dynamically calculates 'is_following' based on the request context.
    """
    uid = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    image_url = serializers.CharField(source='profile.image_url', read_only=True)
    bio = serializers.CharField(source='profile.bio', read_only=True)
    is_me = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    def get_is_me(self, obj):
        """
        Checks if the user object ('obj') is the same as the user making the request.
        """
        request_user = self.context.get('request').user
        return request_user.is_authenticated and request_user == obj

    def get_is_following(self, obj):
        """
        Checks if the current request user is following the user object ('obj').
        'obj' here is the user instance being serialized (the post's author).
        """
        request_user = self.context.get('request').user
        if not request_user or not request_user.is_authenticated:
            return False
        if request_user == obj:
            return False
        return Follow.objects.filter(follower=request_user, following=obj).exists()

class UserProfileReadSerializer(UserProfileSerializer):
    feed_images = serializers.SerializerMethodField()

    def get_feed_images(self, obj):
        return Post.objects.get_first_image_urls_for_user(obj)



class SocialLoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserLoginSerializer()


class FollowResponseSerializer(serializers.Serializer):
    """
    팔로우/언팔로우 액션 후의 응답을 위한 Serializer입니다.
    """
    is_following = serializers.BooleanField(help_text="현재 사용자의 팔로우 여부")
    followers_count = serializers.IntegerField(help_text="대상 유저의 팔로워 수")
    following_count = serializers.IntegerField(help_text="대상 유저의 팔로잉 수")


class UsernameUpdateSerializer(serializers.ModelSerializer):
    """
    A serializer for updating the username, with length and time-based constraints.
    """

    class Meta:
        model = get_user_model()
        fields = ['username']
        extra_kwargs = {
            'username': {
                'required': True,
                'allow_blank': False
            }
        }

    def validate_username(self, value):
        """
        Performs custom validation for the username.
        - Length validation (5-30 characters).
        - Uniqueness is handled by the model field's `unique=True`.
        - Prevents updating to the same username as the current one.
        """
        if not (5 <= len(value) <= 30):
            raise serializers.ValidationError("Username must be between 5 and 30 characters long.")

        if self.instance and self.instance.username == value:
            raise serializers.ValidationError(
                "This is the same as your current username. Please choose a different one.")

        return value

    def validate(self, data):
        """
        Object-level validation to check if the user is allowed to change their username
        based on the last change date.
        """
        user = self.instance
        if not user.can_change_username():
            # Calculate when the user can change it next
            next_change_date = (user.username_last_changed_at + timedelta(days=30)).strftime("%Y-%m-%d")
            raise serializers.ValidationError(
                f"You can only change your username once every 30 days. You can change it again after {next_change_date}."
            )
        return data

    def update(self, instance, validated_data):
        """
        Custom update method to set the username change flags and timestamp.
        """
        instance.username = validated_data.get('username', instance.username)
        instance.is_username_changed = True
        instance.username_last_changed_at = datetime.now(UTC)
        instance.save(update_fields=['username', 'is_username_changed', 'username_last_changed_at'])
        return instance


class UserProfileImageFileInfoSerializer(serializers.Serializer):
    file_name = serializers.CharField()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'image_url']

    def validate(self, data):
        known_fields = set(self.fields.keys())
        input_fields = set(self.initial_data.keys())
        extra_fields = input_fields - known_fields

        if extra_fields:
            raise serializers.ValidationError(
                f"Unexpected field(s) provided: {', '.join(extra_fields)}"
            )

        return data
