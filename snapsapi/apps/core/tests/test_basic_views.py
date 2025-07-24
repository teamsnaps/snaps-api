import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestHomeView:
    """Tests for the home view (/)"""

    def test_home_should_return_200_ok(self, api_client):
        """GET / - Test home endpoint"""
        url = reverse('home')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == "Snaps API is running!"


@pytest.mark.django_db
class TestHealthCheckView:
    """Tests for the health_check view (/core/health/)"""

    def test_health_check_should_return_200_ok(self, api_client):
        """GET /core/health/ - Test health check endpoint"""
        url = reverse('core:health_check')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'ok'