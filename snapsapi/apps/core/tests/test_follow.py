import pytest
from django.urls import reverse
from rest_framework import status

from snapsapi.apps.core.models import Follow


@pytest.mark.django_db
class TestFollowModel:
    """Tests for the Follow model and its signal handlers"""

    def test_follow_creation_increments_counts(self, user1, user2):
        """Test that creating a follow relation increments the following_count and followers_count"""
        # Initial counts should be 0
        assert user1.following_count == 0
        assert user2.followers_count == 0
        
        # Create a follow relation
        Follow.objects.create(follower=user1, following=user2)
        
        # Refresh users from the database
        user1.refresh_from_db()
        user2.refresh_from_db()
        
        # Counts should be incremented
        assert user1.following_count == 1
        assert user2.followers_count == 1

    def test_follow_deletion_decrements_counts(self, user1, user2, follow_relation):
        """Test that deleting a follow relation decrements the following_count and followers_count"""
        # Refresh users from the database to get the updated counts after fixture creation
        user1.refresh_from_db()
        user2.refresh_from_db()
        
        # Initial counts should be 1 because of the follow_relation fixture
        assert user1.following_count == 1
        assert user2.followers_count == 1
        
        # Delete the follow relation
        follow_relation.delete()
        
        # Refresh users from the database
        user1.refresh_from_db()
        user2.refresh_from_db()
        
        # Counts should be decremented
        assert user1.following_count == 0
        assert user2.followers_count == 0

    def test_follow_uniqueness_constraint(self, user1, user2, follow_relation):
        """Test that a user cannot follow another user more than once"""
        # Attempt to create a duplicate follow relation
        with pytest.raises(Exception):  # This should raise an IntegrityError
            Follow.objects.create(follower=user1, following=user2)


@pytest.mark.django_db
class TestFollowToggleView:
    """Tests for the FollowToggleView in the users app (/api/users/{user_uid}/follow/)"""

    def test_follow_toggle_create_should_return_200_ok(self, jwt_client, user1, user2):
        """POST /api/users/{user_uid}/follow/ - Test following a user"""
        url = reverse('users:user-follow-toggle', kwargs={'user_uid': user2.uid})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_following'] is True
        assert response.data['followers_count'] == 1
        
        # Verify the follow relation was created in the database
        assert Follow.objects.filter(follower=user1, following=user2).exists()
        
        # Verify the counts were updated
        user1.refresh_from_db()
        user2.refresh_from_db()
        assert user1.following_count == 1
        assert user2.followers_count == 1

    def test_follow_toggle_delete_should_return_200_ok(self, jwt_client, user1, user2, follow_relation):
        """POST /api/users/{user_uid}/follow/ - Test unfollowing a user"""
        url = reverse('users:user-follow-toggle', kwargs={'user_uid': user2.uid})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_following'] is False
        assert response.data['followers_count'] == 0
        
        # Verify the follow relation was deleted from the database
        assert not Follow.objects.filter(follower=user1, following=user2).exists()
        
        # Verify the counts were updated
        user1.refresh_from_db()
        user2.refresh_from_db()
        assert user1.following_count == 0
        assert user2.followers_count == 0

    def test_follow_toggle_unauthenticated_should_return_401_unauthorized(self, api_client, user2):
        """POST /api/users/{user_uid}/follow/ - Test following a user without authentication"""
        url = reverse('users:user-follow-toggle', kwargs={'user_uid': user2.uid})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED