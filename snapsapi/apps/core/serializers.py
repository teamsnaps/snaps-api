from rest_framework import serializers as s

from snapsapi.apps.core.models import Story, Post, Tag


class StorySerializer(s.ModelSerializer):
    class Meta:
        model = Story
        fields = []


class ReadPostSerializer(s.ModelSerializer):
    tags = s.ListField(
        child=s.CharField(), required=False, write_only=True
    )
    tags_names = s.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ['uid', 'caption', 'images', 'tags', 'tags_names']

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags_data:
            tag_objs = []
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                tag_objs.append(tag)
            instance.tags.set(tag_objs)
        return instance

    def get_tags_names(self, obj):
        # ManyRelatedManager를 쿼리셋으로 뽑아서 이름 리스트로 반환
        return list(obj.tags.values_list('name', flat=True))


class WritePostSerializer(s.ModelSerializer):
    tags = s.ListField(
        child=s.CharField(), required=False, write_only=True
    )

    # tags_names = s.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ['uid', 'caption', 'images', 'tags']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        tag_objs = []
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tag_objs.append(tag)
        post.tags.set(tag_objs)
        return post
    #
    # def update(self, instance, validated_data):
    #     tags_data = validated_data.pop('tags', [])
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     if tags_data:
    #         tag_objs = []
    #         for tag_name in tags_data:
    #             tag, _ = Tag.objects.get_or_create(name=tag_name)
    #             tag_objs.append(tag)
    #         instance.tags.set(tag_objs)
    #     return instance
    #
    # def get_tags_names(self, obj):
    #     # ManyRelatedManager를 쿼리셋으로 뽑아서 이름 리스트로 반환
    #     return list(obj.tags.values_list('name', flat=True))


class PostSerializer(s.ModelSerializer):
    tags = s.ListField(
        child=s.CharField(), required=False, write_only=True
    )

    # tags_names = s.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ['uid', 'caption', 'images', 'tags']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        tag_objs = []
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tag_objs.append(tag)
        post.tags.set(tag_objs)
        return post

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags_data:
            tag_objs = []
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                tag_objs.append(tag)
            instance.tags.set(tag_objs)
        return instance

    # def get_tags_names(self, obj):
    #     # ManyRelatedManager를 쿼리셋으로 뽑아서 이름 리스트로 반환
    #     return list(obj.tags.values_list('name', flat=True))
