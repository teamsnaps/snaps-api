from rest_framework import serializers as s

from snapsapi.apps.core.models import Story

class StorySerializer(s.ModelSerializer):
    class Meta:
        model = Story
        fields = []
