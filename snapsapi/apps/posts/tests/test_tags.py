import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from snapsapi.apps.posts.models import Tag


@pytest.mark.django_db
class TestTagListView:
    """Tests for the TagListView endpoint at /api/posts/tags/"""

    def test_list_tags_returns_200_ok(self, api_client, tag1):
        """GET /api/posts/tags/ - Test that the endpoint returns a 200 OK status."""
        url = reverse('posts:tags-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_list_tags_returns_correct_data(self, api_client, tag1):
        """GET /api/posts/tags/ - Test that the endpoint returns the correct tag data."""
        url = reverse('posts:tags-list')
        response = api_client.get(url)
        data = response.json()

        assert len(data) >= 1
        assert any(tag['uid'] == str(tag1.uid) for tag in data)
        assert any(tag['name'] == tag1.name for tag in data)
        assert any(tag['image_url'] == tag1.image_url for tag in data)
        assert any(tag['is_featured'] == tag1.is_featured for tag in data)

    def test_list_tags_with_multiple_tags(self, api_client, tag1):
        """GET /api/posts/tags/ - Test that the endpoint returns multiple tags correctly."""
        # Create additional tags with different is_featured values
        tag2 = Tag.objects.create(name="another_tag", is_featured=True)
        tag3 = Tag.objects.create(name="third_tag", is_featured=True)

        url = reverse('posts:tags-list')
        response = api_client.get(url)
        data = response.json()

        assert len(data) >= 3
        tag_names = [tag['name'] for tag in data]
        assert tag1.name in tag_names
        assert tag2.name in tag_names
        assert tag3.name in tag_names

        # Check is_featured values
        tag1_data = next((tag for tag in data if tag['name'] == tag1.name), None)
        tag2_data = next((tag for tag in data if tag['name'] == tag2.name), None)
        tag3_data = next((tag for tag in data if tag['name'] == tag3.name), None)

        assert tag1_data['is_featured'] == tag1.is_featured
        assert tag2_data['is_featured'] == True
        assert tag3_data['is_featured'] == True

    def test_list_tags_with_no_tags(self, api_client):
        """GET /api/posts/tags/ - Test that the endpoint returns an empty list when no tags exist."""
        # Delete all existing tags
        Tag.objects.all().delete()

        url = reverse('posts:tags-list')
        response = api_client.get(url)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert len(data) == 0
        assert isinstance(data, list)

    def test_list_tags_anonymous_access(self, api_client, tag1):
        """GET /api/posts/tags/ - Test that the endpoint is accessible without authentication."""
        url = reverse('posts:tags-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) >= 1
