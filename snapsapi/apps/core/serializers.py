from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from snapsapi.apps.users.serializers import UserSerializer
from snapsapi.apps.core.models import Collection, CollectionMember
from snapsapi.apps.posts.models import Post

User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uid', 'username']


class CollectionMemberSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='user'
    )

    class Meta:
        model = CollectionMember
        fields = ['id', 'user', 'user_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class CollectionPostSerializer(serializers.ModelSerializer):
    """Simplified Post serializer for use in Collection serializers"""
    first_image = serializers.SerializerMethodField()

    class Meta:
        model = Post  # Will be set dynamically when imported
        fields = ['uid', 'caption', 'first_image', 'created_at']
        read_only_fields = ['uid', 'caption', 'first_image', 'created_at']

    def get_first_image(self, obj):
        first_image = obj.images.order_by('order').first()
        if first_image:
            return first_image.url
        return None


class CollectionReadSerializer(serializers.ModelSerializer):
    owner = UserInfoSerializer(read_only=True)
    posts = serializers.SerializerMethodField()
    members = CollectionMemberSerializer(many=True, read_only=True)
    posts_count = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            'uid', 'name', 'description', 'owner', 'posts', 'members',
            'is_public', 'created_at', 'updated_at', 'posts_count', 'members_count'
        ]
        read_only_fields = ['uid', 'created_at', 'updated_at']

    def get_posts(self, obj):
        from snapsapi.apps.core.serializers import CollectionPostSerializer
        return CollectionPostSerializer(obj.posts.all(), many=True).data

    def get_posts_count(self, obj):
        return obj.posts.count()

    def get_members_count(self, obj):
        return obj.members.count()


class CollectionWriteSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Collection
        fields = ['uid', 'name', 'description', 'owner', 'is_public', 'created_at', 'updated_at']
        read_only_fields = ['uid', 'created_at', 'updated_at']

    def create(self, validated_data):
        return Collection.objects.create_collection(
            owner=validated_data['owner'],
            name=validated_data['name'],
            description=validated_data.get('description', ''),
            is_public=validated_data.get('is_public', True)
        )

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.is_public = validated_data.get('is_public', instance.is_public)
        instance.save()
        return instance

    def to_representation(self, instance):
        return CollectionReadSerializer(instance, context=self.context).data
