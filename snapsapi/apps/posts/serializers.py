from django.contrib.auth import get_user, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from snapsapi.apps.users.serializers import UserSerializer, UserProfileSerializer
from snapsapi.apps.posts.models import Post, PostImage, Tag
from snapsapi.apps.likes.models import PostLike
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError

user = get_user_model()


class PostImageURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        # PostImage 모델에 'url' 필드가 있다고 가정합니다.
        fields = ['url']


class ImageURLSerializer(serializers.Serializer):
    """A simple serializer to validate objects with a 'url' key."""
    url = serializers.URLField()


# GET 요청 (목록 조회) 시 사용할 메인 Serializer
class PostListSerializer(serializers.ModelSerializer):
    # 각 중첩 객체를 만들기 위해 SerializerMethodField를 사용합니다.
    metadata = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)
    context = serializers.SerializerMethodField(read_only=True)

    # images 필드는 PostImageURLSerializer를 사용하여 배열 형태로 만듭니다.
    # Post 모델의 PostImage 관련 필드(related_name)가 'images'라고 가정합니다.
    images = PostImageURLSerializer(many=True, read_only=True)

    # 이 필드들은 View의 get_queryset에서 annotate로 추가된 값들을 사용합니다.
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = (
            'metadata',
            'profile',
            'images',
            'context',
            'created_at',
            'updated_at',
            'likes_count',
            'comments_count',
        )

    def get_metadata(self, obj):
        """metadata 객체를 구성합니다."""
        return {
            "post_uid": obj.uid,
            "user_uid": obj.user.uid
        }

    def get_profile(self, obj):
        """게시글 작성자의 user 객체를 이용해 profile 객체를 구성합니다."""
        user = obj.user
        profile_image = None
        # User의 Profile에 image 필드가 있고, 이 값이 리스트 형태일 경우 첫 번째 항목을 사용합니다.
        if hasattr(user, 'profile') and user.profile.image:
            if isinstance(user.profile.image, list) and len(user.profile.image) > 0:
                profile_image = user.profile.image[0]
            # 문자열일 경우 그대로 사용합니다.
            elif isinstance(user.profile.image, str):
                profile_image = user.profile.image

        return {
            "username": user.username,
            "image": profile_image
        }

    def get_context(self, obj):
        """context 객체를 구성합니다."""
        # prefetch_related와 함께 사용하면 효율적입니다.
        tag_names = list(obj.tags.values_list('name', flat=True))
        return {
            "username": obj.user.username,
            "caption": obj.caption,
            "tags": tag_names
        }


class PostCreateSerializer(serializers.Serializer):
    caption = serializers.CharField(
        allow_blank=True,
        help_text=_("게시글에 대한 설명을 자유롭게 작성해주세요. 비워두어도 괜찮습니다.")
    )
    images = ImageURLSerializer(
        many=True,
        write_only=True,
        help_text=_("게시글에 추가할 이미지 목록입니다. `[{'url': 'https://...'}]` 형식의 배열이어야 합니다.")
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        allow_empty=True,
        write_only=True,
        help_text=_("게시글을 분류할 태그를 입력합니다. 예: `['여행', '풍경']`")
    )

    def create(self, validated_data):
        user = self.context['request'].user
        caption = validated_data.get('caption', '')
        images = [item['url'] for item in validated_data.get('images', [])]
        tags = validated_data.get('tags', [])

        post = Post.objects.create_post(user, caption, images, tags)
        return post


class PostUpdateSerializer(serializers.ModelSerializer):
    caption = serializers.CharField(allow_blank=True, required=False, help_text="게시글 내용")
    tags = serializers.ListField(child=serializers.CharField(max_length=255), required=False, help_text="태그 문자열 리스트")
    images = serializers.ListField(child=serializers.URLField(), required=False, help_text="이미지 URL 리스트")
    is_public = serializers.BooleanField(required=False, help_text="공개 여부")
    is_active = serializers.BooleanField(required=False, help_text="활성 여부")
    is_deleted = serializers.BooleanField(required=False, help_text="삭제 여부")

    class Meta:
        model = Post
        fields = [
            'caption',
            'tags',
            'images',
            'is_public',
            'is_active',
            'is_deleted',
        ]

    def validate_tags(self, value):
        """
        # Ensure tags is a list of non-empty strings
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list.")
        for tag in value:
            if not isinstance(tag, str) or not tag.strip():
                raise serializers.ValidationError("Each tag must be a non-empty string.")
        return value

    def validate_images(self, value):
        """
        # Ensure images is a list of valid URLs
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Images must be a list.")
        validator = URLValidator()
        for url in value:
            try:
                validator(url)
            except DjangoValidationError:
                raise serializers.ValidationError(f"Invalid URL: '{url}'")
        return value

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        images_data = validated_data.pop('images', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if images_data is not None:
            instance.delete_images()
            instance.attach_images(images_data)

        if tags_data is not None:
            instance.update_tags(tags_data)

        instance.save()
        return instance

    def to_representation(self, instance):
        """
        객체를 직렬화하여 API 응답 형식으로 변환합니다.
        """
        # return {
        #     "uid": str(instance.uid),
        #     "caption": instance.caption,
        #     "images": [img.url for img in instance.images.all()],
        #     "tags": [tag.name for tag in instance.tags.all()],
        #     "is_public": instance.is_public,
        #     "is_active": instance.is_active,
        #     "is_deleted": instance.is_deleted,
        # }
        return {
            "uid": str(instance.uid),
            "caption": instance.caption,
            "images": [img.url for img in instance.images.all()],
            "tags": [tag.name for tag in instance.tags.all()]
        }


# --- User 정보를 위한 간단한 Serializer ---
# 이 Serializer는 Post 안에 작성자 정보를 표현하기 위해 사용됩니다.
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = ['uid', 'username']  # 필요에 따라 'profile_image' 등 추가 가능


class PostReadSerializer(serializers.ModelSerializer):
    """
    Serializer for post detail view.
    Returns data in the requested nested JSON structure (metadata, user, etc.).
    """
    # These are declared for clarity, but their final values are constructed in to_representation.
    user = UserProfileSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        # Include all fields needed to build the final representation.
        fields = [
            'uid',
            'user',
            'caption',
            'images',
            'tags',
            'likes_count',
            'comments_count',
            'is_liked',
            'is_public',
            'created_at',
            'updated_at',
        ]

    def get_images(self, post):
        """
        Returns a list of image objects for the post, formatted as [{"url": "..."}].
        """
        # Assumes post.images.all() returns a queryset of PostImage objects, each with a 'url' attribute.
        return [{'url': image.url} for image in post.images.all()]

    def get_is_liked(self, post):
        """
        Returns True/False whether the user from the request context has liked
        the current post object.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if a PostLike entry exists for the given post and user.
            return PostLike.objects.filter(post=post, user=request.user).exists()
        return False

    def to_representation(self, instance):
        """
        Overrides the default output to create the requested nested JSON structure.
        """
        # 1. Generate the base representation using the fields defined in `Meta.fields`.
        data = super().to_representation(instance)

        # 2. Correctly generate the 'user' data by passing the context to UserProfileSerializer.
        user_serializer = UserProfileSerializer(instance.user, context=self.context)
        user_data = user_serializer.data

        # 3. Assemble the final, restructured dictionary.
        restructured_data = {
            "metadata": {
                "post_uid": instance.uid,  # Get directly from the post instance.
                "user_uid": instance.user.uid  # Get directly from the related user instance.
            },
            "user": user_data,  # The user data generated in step 2.
            "images": data.get('images'),  # Get from the base representation.
            "caption": data.get('caption'),
            "tags": data.get('tags'),
            "likes_count": data.get('likes_count'),
            "comments_count": data.get('comments_count'),
            "is_liked": data.get('is_liked'),
            "is_public": data.get('is_public'),
            "created_at": data.get('created_at'),
            "updated_at": data.get('updated_at')
        }

        return restructured_data


class PostDeleteSerializer(serializers.Serializer):
    pass


class FileInfoSerializer(serializers.Serializer):
    file_name = serializers.CharField()
    file_type = serializers.CharField()


class PresignedURLRequestSerializer(serializers.Serializer):
    files = FileInfoSerializer(many=True)
