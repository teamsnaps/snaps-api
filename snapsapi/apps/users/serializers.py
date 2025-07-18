from django.contrib.auth import get_user_model
from rest_framework import serializers
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from datetime import timezone, datetime, UTC, timedelta

from snapsapi.apps.posts.models import Post
from snapsapi.apps.users.models import Profile
from snapsapi.apps.core.models import Follow


class UserSerializer(serializers.Serializer):
    """
    User profile information for display purposes.
    Dynamically calculates 'is_following' based on the request context.
    """
    uid = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    image_url = serializers.CharField(source='profile.image_url', read_only=True, default='/media/users/default/user.png')
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

# class UserLoginSerializer(UserSerializer):
#     email = serializers.EmailField(read_only=True)
#     first_name = serializers.CharField(read_only=True)
#     last_name = serializers.CharField(read_only=True)
#     is_username_changed = serializers.BooleanField(read_only=True, default=False)
#
#     def to_representation(self, instance):
#         # 먼저 부모 클래스의 to_representation을 호출
#         representation = super().to_representation(instance)
#
#         # 추가 필드 값 설정
#         representation['email'] = instance.email
#         representation['first_name'] = instance.first_name
#         representation['last_name'] = instance.last_name
#
#         # is_username_changed 필드가 존재하는 경우 추가
#         if hasattr(instance, 'is_username_changed'):
#             representation['is_username_changed'] = instance.is_username_changed
#
#         return representation
class UserLoginSerializer(serializers.Serializer):
    """
    Comprehensive user information for login responses.
    """
    # UserSerializer 필드
    # uid = serializers.CharField(read_only=True)
    # username = serializers.CharField(read_only=True)
    # image_url = serializers.CharField(source='profile.image_url', read_only=True, default='/media/users/default/user.png')
    # bio = serializers.CharField(source='profile.bio', read_only=True)
    # is_me = serializers.SerializerMethodField()
    # is_following = serializers.SerializerMethodField()
    # email = serializers.EmailField(read_only=True)
    # first_name = serializers.CharField(read_only=True)
    # last_name = serializers.CharField(read_only=True)
    is_username_changed = serializers.BooleanField(read_only=True, default=False)

    def get_is_me(self, obj):
        request_user = self.context.get('request').user
        return request_user.is_authenticated and request_user == obj

    def get_is_following(self, obj):
        request_user = self.context.get('request').user
        if not request_user or not request_user.is_authenticated:
            return False
        if request_user == obj:
            return False
        return Follow.objects.filter(follower=request_user, following=obj).exists()



class UserProfileSerializer(serializers.Serializer):
    """
    User profile information for display purposes.
    Dynamically calculates 'is_following' based on the request context.
    """
    metadata = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(source='*', read_only=True)
    posts_count = serializers.IntegerField(read_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            'metadata',
            'user',
            'posts_count',
            'followers_count',
            'following_count',
            'images',
        )

    def get_metadata(self, obj):
        return {
            'user_uid': obj.uid
        }

    def get_images(self, obj):
        return {
            "feed_images": Post.objects.get_posts_by_user(obj)
        }


class SocialLoginWriteSerializer(SocialLoginSerializer):
    access_token = serializers.CharField()
    provider = serializers.ChoiceField(choices=['google', 'kakao', 'naver'])


class SocialLoginReadSerializer(SocialLoginSerializer):
    provider = serializers.ChoiceField(choices=['google', 'kakao', 'naver'])


# class UserLoginSerializer(serializers.Serializer):
#     uid = serializers.CharField()
#     username = serializers.CharField()
#     email = serializers.EmailField()
#     first_name = serializers.CharField()
#     last_name = serializers.CharField()
#
#
# class SocialLoginResponseSerializer(serializers.Serializer):
#     access = serializers.CharField()
#     refresh = serializers.CharField()
#     user = UserLoginSerializer()

class SocialLoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserLoginSerializer()
    access_expiration = serializers.DateTimeField()
    refresh_expiration = serializers.DateTimeField()


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
        - Length validation (5-20 characters).
        - Character validation (only uppercase letters, lowercase letters, numbers, '.', '_').
        - Uniqueness is handled by the model field's `unique=True`.
        - Prevents updating to the same username as the current one.
        """
        if not (5 <= len(value) <= 20):
            raise serializers.ValidationError("Username must be between 5 and 20 characters long.")

        import re
        if not re.match(r'^[a-z0-9._]+$', value):
            # raise serializers.ValidationError("Username can only contain uppercase letters, lowercase letters, numbers, periods, and underscores.")
            raise serializers.ValidationError("사용자명은 영문소문자, 숫자, 마침표(.), 밑줄(_)만 사용 가능합니다.")

        if self.instance and self.instance.username == value:
            raise serializers.ValidationError(
                # "This is the same as your current username. Please choose a different one.")
                "현재 사용 중인 사용자명과 동일합니다. 다른 사용자명을 선택해 주세요.")

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
                # f"You can only change your username once every 30 days. You can change it again after {next_change_date}."
                f"사용자 이름은 30일에 한 번만 변경 가능합니다. {next_change_date} 이후에 다시 수정해주세요."
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
