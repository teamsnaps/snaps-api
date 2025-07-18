from typing import Any

from django.contrib.auth import get_user, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from snapsapi.apps.users.serializers import SocialLoginResponseSerializer, UserSerializer
from snapsapi.apps.posts.models import Post, PostImage, Tag
from snapsapi.apps.likes.models import PostLike
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError

user = get_user_model()


class PostImageURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        # Assumes that the PostImage model has a 'url' field.
        fields = ['url']


class PostImageURLInputSerializer(serializers.Serializer):
    """A serializer to validate post image URL input objects with a 'url' key."""
    url = serializers.CharField()


class PostReadSerializer(serializers.ModelSerializer):
    """
    A Serializer used for retrieving posts.
    It serializes all fields, including the user's 'like' status and 'collection' status.
    """
    metadata = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    is_liked = serializers.SerializerMethodField()
    is_collected = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'metadata',
            'uid',
            'user',
            'caption',
            'images',
            'tags',
            'likes_count',
            'comments_count',
            'is_liked',
            'is_collected',
            'is_public',
            'created_at',
            'updated_at',
        ]

    def get_metadata(self, obj):
        return {"post_uid": obj.uid, "user_uid": obj.user.uid}

    def get_images(self, obj: object) -> list[dict[str, Any]] | list[Any]:
        return [{'url': image.url} for image in obj.images.all()] if hasattr(obj, 'images') else []

    def get_is_liked(self, post):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(post=post, user=request.user).exists()
        return False

    def get_is_collected(self, post):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from snapsapi.apps.core.models import Collection
            # Get the user's default collection
            default_collection = Collection.objects.filter(owner=request.user, name='default').first()
            if default_collection:
                # Check if the post is in the default collection
                return default_collection.posts.filter(pk=post.pk).exists()
        return False


class PostWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating posts.
    """
    caption = serializers.CharField(
        allow_blank=True,
        required=False,
        help_text=_("Write a description for your post. It can be left blank.")
    )
    images = PostImageURLInputSerializer(
        many=True,
        write_only=True,
        required=False,
        help_text=_("List of images to add to the post. Must be an array in the format `[{'url': 'https://...'}]`")
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=255),
        allow_empty=True,
        write_only=True,
        required=False,
        help_text=_("Enter tags to categorize your post. Example: `['travel', 'landscape']`")
    )
    is_public = serializers.BooleanField(required=False, help_text="Whether the post is public")
    is_active = serializers.BooleanField(required=False, help_text="Whether the post is active")
    is_deleted = serializers.BooleanField(required=False, help_text="Whether the post is deleted")

    class Meta:
        model = Post
        fields = [
            'caption',
            'images',
            'tags',
            'is_public',
            'is_active',
            'is_deleted',
        ]

    def validate_tags(self, value):
        """
        Ensure tags is a list of non-empty strings
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list.")
        for tag in value:
            if not isinstance(tag, str) or not tag.strip():
                raise serializers.ValidationError("Each tag must be a non-empty string.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        caption = validated_data.get('caption', '')
        images = [item['url'] for item in validated_data.get('images', [])]
        tags = validated_data.get('tags', [])
        post = Post.objects.create_post(request.user, caption, images, tags)
        return post

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        tags_data = validated_data.pop('tags', None)

        # Update simple fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update images if provided
        if images_data is not None:
            instance.delete_images()
            instance.attach_images([item['url'] for item in images_data])

        # Update tags if provided
        if tags_data is not None:
            instance.update_tags(tags_data)

        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Convert the object to a representation suitable for API responses.
        """
        return {
            "uid": str(instance.uid),
            "caption": instance.caption,
            "images": [{'url': img.url} for img in instance.images.all()],
            "tags": [tag.name for tag in instance.tags.all()],
            "is_public": instance.is_public,
            "is_active": instance.is_active,
            "is_deleted": instance.is_deleted,
        }


# Main Serializer used for GET requests (list view)
class PostListSerializer(serializers.ModelSerializer):
    # Using SerializerMethodField to create each nested object
    metadata = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)
    context = serializers.SerializerMethodField(read_only=True)

    # The images field uses PostImageURLSerializer to create an array format
    # Assumes that the PostImage related field (related_name) in the Post model is 'images'
    images = PostImageURLSerializer(many=True, read_only=True)

    # These fields use values added by annotate in the View's get_queryset
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
        """Constructs the metadata object."""
        return {
            "post_uid": obj.uid,
            "user_uid": obj.user.uid
        }

    def get_profile(self, obj):
        """Constructs the profile object using the post author's user object."""
        user = obj.user
        profile_image = None
        # If the User's Profile has an image field and this value is a list, use the first item.
        if hasattr(user, 'profile') and user.profile.image:
            if isinstance(user.profile.image, list) and len(user.profile.image) > 0:
                profile_image = user.profile.image[0]
            # If it's a string, use it as is.
            elif isinstance(user.profile.image, str):
                profile_image = user.profile.image

        return {
            "username": user.username,
            "image": profile_image
        }

    def get_context(self, obj):
        """Constructs the context object."""
        # More efficient when used with prefetch_related.
        tag_names = list(obj.tags.values_list('name', flat=True))
        return {
            "username": obj.user.username,
            "caption": obj.caption,
            "tags": tag_names
        }


# PostUpdateSerializer was removed and its functionality consolidated into PostWriteSerializer


# --- Simple Serializer for User information ---
# This Serializer is used to represent author information within a Post.
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = ['uid', 'username']  # Can add 'profile_image' etc. as needed


# PostDeleteSerializer was removed as it was empty and not used


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for the Tag model.
    """
    class Meta:
        model = Tag
        fields = ['uid', 'name', 'image_url', 'is_featured']


class FileInfoSerializer(serializers.Serializer):
    file_name = serializers.CharField()
    file_type = serializers.CharField()


class PresignedURLRequestSerializer(serializers.Serializer):
    files = FileInfoSerializer(many=True)
