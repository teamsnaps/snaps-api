from rest_framework import serializers
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
            "uid": str(instance.pk),
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
        return {
            "uid": str(instance.uid),
            "caption": instance.caption,
            "images": [img.url for img in instance.images.all()],
            "tags": [tag.name for tag in instance.tags.all()],
            "is_public": instance.is_public,
            "is_active": instance.is_active,
            "is_deleted": instance.is_deleted,
        }



class FileInfoSerializer(serializers.Serializer):
    file_name = serializers.CharField()
    file_type = serializers.CharField()


class PresignedURLRequestSerializer(serializers.Serializer):
    files = FileInfoSerializer(many=True)
