from rest_framework import serializers
from snapsapi.apps.posts.models import Post
from snapsapi.apps.comments.models import Comment
from snapsapi.apps.users.serializers import UserSerializer

from rest_framework import serializers

from snapsapi.apps.comments.models import Comment
from snapsapi.apps.posts.models import Post


class CommentReadSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving comments (GET).
    Includes author information and replies (nested comments).
    """
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'uid',
            'user',
            'content',
            'created_at',
            'parent',
            'replies',
        ]
        read_only_fields = fields

    def get_replies(self, instance):
        """
        Recursively serializes the replies (nested comments).
        """
        if instance.replies.exists():
            return CommentReadSerializer(instance.replies.all(), many=True, context=self.context).data
        return []


class CommentCreateSerializer(serializers.Serializer):
    """
    Serializer for creating comments (POST).
    Receives a post object from the View to create a comment.
    """
    # 1. The post_uid field is removed because we get this information from the URL.
    content = serializers.CharField(max_length=255, help_text="Comment content")
    parent_uid = serializers.UUIDField(required=False, allow_null=True, write_only=True, help_text="UID of the parent comment if this is a reply")

    def validate(self, data):
        """
        Data validation:
        - If a parent comment exists, verify it belongs to the post specified in the URL.
        """
        parent_uid = data.get('parent_uid')
        post = self.context.get('post')  # Post object passed from the View

        if parent_uid:
            try:
                # Check if the parent comment exists and belongs to the current post
                parent_comment = Comment.objects.get(uid=parent_uid, post=post)
                data['parent'] = parent_comment  # Add the object to data for use in the create method
            except Comment.DoesNotExist:
                raise serializers.ValidationError({'parent_uid': 'Parent comment not found or belongs to a different post.'})
        else:
            data['parent'] = None

        return data

    def create(self, validated_data):
        """
        Creates a Comment object with the validated data.
        """
        user = self.context['request'].user
        post = self.context['post']  # Using the post object provided by the View in the context
        content = validated_data.get('content')
        parent = validated_data.get('parent')  # Parent object added in the validate method

        comment = Comment.objects.create_comment(
            user=user,
            post=post,
            content=content,
            parent=parent
        )
        return comment

    def to_representation(self, instance):
        """
        Converts the created object to API response format.
        """
        return CommentReadSerializer(instance, context=self.context).data


class CommentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating comments (PATCH).
    Restricts updates to only the 'content' field.
    """

    class Meta:
        model = Comment
        fields = ['content']
        # Additional constraints can be set for the content field
        extra_kwargs = {
            'content': {
                'required': True,  # The content field is required when updating
                'allow_blank': False  # Empty strings are not allowed
            }
        }

    def update(self, instance, validated_data):
        """
        Updates the content of the comment.
        Uses the default update behavior of ModelSerializer.
        """
        # Ownership verification is typically handled in the View.
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Converts the modified object to API response format.
        Uses the read-only Serializer to provide a consistent response.
        """
        return CommentReadSerializer(instance, context=self.context).data


class CommentDeleteSerializer:
    pass
