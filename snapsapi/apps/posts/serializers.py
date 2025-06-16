from rest_framework import serializers

from snapsapi.apps.users.serializers import UserSerializer
from snapsapi.apps.posts.models import Post, PostImage, Tag
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError


class PostCreateSerializer(serializers.Serializer):
    caption = serializers.CharField(
        allow_blank=True,
        help_text="게시글 내용"
    )
    images = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        help_text="이미지의 URL 리스트"
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        allow_empty=True,
        write_only=True,
        help_text="태그 문자열 리스트"
    )

    def create(self, validated_data):
        user = self.context['request'].user
        caption = validated_data.get('caption', '')
        images = validated_data.get('images', [])
        tags = validated_data.get('tags', [])

        # Create a Post object
        post = Post.objects.create_post(user, caption, images, tags)
        # post = Post.objects.create(user=user, caption=caption)
        #
        # # Save images
        # post_images = [
        #     PostImage(post=post, url=url, order=i)
        #     for i, url in enumerate(images)
        # ]
        # PostImage.objects.bulk_create(post_images)
        #
        # # Tag processing (get if it already exists, create if it doesn't exist)
        # tag_objs = []
        # for tag_name in tags:
        #     tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
        #     tag_objs.append(tag_obj)
        # post.tags.set(tag_objs)

        return post

    def to_representation(self, instance):
        return {
            "uid": str(instance.uid),
            "caption": instance.caption,
            "images": [img.url for img in instance.images.all()],
            "tags": [tag.name for tag in instance.tags.all()]
        }


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


class PostReadSerializer(serializers.ModelSerializer):
    """
    게시물 상세 조회(GET 요청)를 위한 시리얼라이저입니다.
    읽기 전용(read-only)이며, 게시물과 관련된 모든 주요 정보를 포함합니다.
    """
    # 1. 작성자 정보 (Nested Serializer)
    user = UserSerializer(read_only=True)

    # 2. 연관된 이미지와 태그 목록 (SerializerMethodField 사용)
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    # 3. 상호작용 정보 (좋아요)
    like_count = serializers.SerializerMethodField(help_text="좋아요 개수")
    is_liked = serializers.SerializerMethodField(help_text="현재 사용자가 좋아요를 눌렀는지 여부")

    class Meta:
        model = Post
        fields = [
            'uid',
            'user',
            'caption',
            'images',
            'tags',
            'like_count',
            'is_liked',
            'created_at',
            'updated_at',
        ]

    def get_images(self, post_instance):
        """Post에 연결된 이미지들의 URL 목록을 반환합니다."""
        return [image.url for image in post_instance.images.all()]

    def get_tags(self, post_instance):
        """Post에 연결된 태그들의 이름 목록을 반환합니다."""
        return [tag.name for tag in post_instance.tags.all()]

    def get_like_count(self, post_instance):
        """Post의 좋아요 개수를 반환합니다."""
        # Post 모델에 'likes'라는 related_name이 있다고 가정합니다.
        # 만약 PostLike 모델에서 related_name을 설정하지 않았다면
        # post_instance.postlike_set.count() 로 사용할 수 있습니다.
        return post_instance.likes.count()

    def get_is_liked(self, post_instance):
        """
        요청을 보낸 사용자가 이 Post에 좋아요를 눌렀는지 확인합니다.
        """
        request_user = self.context.get('request').user
        # 로그인하지 않은 사용자는 항상 False를 반환합니다.
        if not request_user or not request_user.is_authenticated:
            return False
        # 'likes' related_name과 user를 사용하여 존재 여부를 확인합니다.
        return post_instance.likes.filter(user=request_user).exists()


class PostDeleteSerializer(serializers.Serializer):
    pass


class FileInfoSerializer(serializers.Serializer):
    file_name = serializers.CharField()
    file_type = serializers.CharField()


class PresignedURLRequestSerializer(serializers.Serializer):
    files = FileInfoSerializer(many=True)
