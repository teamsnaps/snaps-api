from django.contrib.auth import get_user, get_user_model
from rest_framework import serializers

from snapsapi.apps.users.serializers import UserSerializer
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


# --- User 정보를 위한 간단한 Serializer ---
# 이 Serializer는 Post 안에 작성자 정보를 표현하기 위해 사용됩니다.
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = ['uid', 'username'] # 필요에 따라 'profile_image' 등 추가 가능

# --- PostReadSerializer 수정 ---
class PostReadSerializer(serializers.ModelSerializer):
    """
    게시물 상세 조회(GET)를 위한 최적화된 Serializer입니다.
    Post 모델의 필드와 연관된 정보를 효율적으로 반환합니다.
    """
    # 1. Nested Serializer를 사용하여 작성자 정보를 포함시킵니다.
    user = UserInfoSerializer(read_only=True)

    # 2. ManyToMany 관계인 태그와 이미지를 처리합니다.
    #    - images: SerializerMethodField를 사용해 이미지 URL 목록을 반환
    #    - tags: SlugRelatedField를 사용해 태그 이름 목록을 간단히 반환
    images = serializers.SerializerMethodField()
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    # 3. 현재 로그인한 사용자의 좋아요 여부를 확인하기 위한 필드입니다.
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        # 모델에 정의된 필드들을 명시적으로 포함합니다.
        fields = [
            'uid',
            'user',
            'caption',
            'images',          # 메서드로 처리
            'tags',            # SlugRelatedField로 처리
            'likes_count',     # 모델 필드 직접 사용
            'comments_count',  # 모델 필드 직접 사용
            'is_liked',        # 메서드로 처리
            'is_public',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields # 모든 필드를 읽기 전용으로 설정

    def get_images(self, post):
        """
        Post 객체에 연결된 PostImage 객체들의 URL 목록을 반환합니다.
        prefetch_related와 함께 사용될 때 효율적입니다.
        """
        # PostImage 모델에 'post' ForeignKey가 있고, 'url' 필드가 있다고 가정합니다.
        # 이 Post에 연결된 모든 이미지들을 가져옵니다.
        return [image.url for image in post.images.all()]

    def get_is_liked(self, post):
        """
        Context로 전달받은 request의 user가 현재 post 객체에
        좋아요를 눌렀는지 여부를 True/False로 반환합니다.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # PostLike 모델에서 (user, post) 쌍이 존재하는지 확인합니다.
            return PostLike.objects.filter(post=post, user=request.user).exists()
        return False


class PostDeleteSerializer(serializers.Serializer):
    pass


class FileInfoSerializer(serializers.Serializer):
    file_name = serializers.CharField()
    file_type = serializers.CharField()


class PresignedURLRequestSerializer(serializers.Serializer):
    files = FileInfoSerializer(many=True)
