from rest_framework.generics import ListCreateAPIView

from snapsapi.apps.core.serializers import StorySerializer
from snapsapi.apps.core.models import Story


class StoryListCreateView(ListCreateAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
