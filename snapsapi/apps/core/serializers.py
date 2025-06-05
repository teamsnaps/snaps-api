from rest_framework import serializers as s

from snapsapi.apps.core.models import Story, Post, Tag


class StorySerializer(s.ModelSerializer):
    class Meta:
        model = Story
        fields = []


class PostSerializer(s.ModelSerializer):
    tags = s.ListField(
        child=s.CharField(), required=False, write_only=True
    )
    tags_names = s.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ['uid', 'images', 'caption', 'tags', 'tags_names']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        tag_objs = []
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tag_objs.append(tag)
        post.tags.set(tag_objs)
        return post

    def get_tags_names(self, obj):
        # ManyRelatedManager를 쿼리셋으로 뽑아서 이름 리스트로 반환
        return list(obj.tags.values_list('name', flat=True))