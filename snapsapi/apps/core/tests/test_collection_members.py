import pytest
from django.urls import reverse
from rest_framework import status

from snapsapi.apps.core.models import CollectionMember


@pytest.mark.django_db
class TestCollectionMemberView:
    """Tests for the CollectionMemberView (/collections/{uid}/members/{user_uid}/)"""

    def test_add_member_should_return_201_created(self, jwt_client, collection1, user2):
        """POST /collections/{uid}/members/{user_uid}/ - Test adding a member to a collection"""
        url = reverse('collections-members-detail', kwargs={'uid': collection1.uid, 'user_uid': user2.uid})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify the member was added in the database
        assert CollectionMember.objects.filter(collection=collection1, user=user2).exists()

    def test_add_member_by_non_owner_should_return_403_forbidden(self, jwt_client_user2, collection1, user2):
        """POST /collections/{uid}/members/{user_uid}/ - Test adding a member by a non-owner"""
        url = reverse('collections-members-detail', kwargs={'uid': collection1.uid, 'user_uid': user2.uid})
        response = jwt_client_user2.post(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_add_member_that_does_not_exist_should_return_404_not_found(self, jwt_client, collection1):
        """POST /collections/{uid}/members/{user_uid}/ - Test adding a non-existent member"""
        url = reverse('collections-members-detail', kwargs={'uid': collection1.uid, 'user_uid': '00000000-0000-0000-0000-000000000000'})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_member_that_is_already_a_member_should_return_400_bad_request(self, jwt_client, collection1, user2, collection_member):
        """POST /collections/{uid}/members/{user_uid}/ - Test adding a member that is already a member"""
        # First, add user2 as a member of collection1
        CollectionMember.objects.create(collection=collection1, user=user2)
        
        url = reverse('collections-members-detail', kwargs={'uid': collection1.uid, 'user_uid': user2.uid})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_member_should_return_204_no_content(self, jwt_client, collection1, user2):
        """DELETE /collections/{uid}/members/{user_uid}/ - Test removing a member from a collection"""
        # First, add user2 as a member of collection1
        CollectionMember.objects.create(collection=collection1, user=user2)
        
        url = reverse('collections-members-detail', kwargs={'uid': collection1.uid, 'user_uid': user2.uid})
        response = jwt_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the member was removed from the database
        assert not CollectionMember.objects.filter(collection=collection1, user=user2).exists()

    def test_remove_member_by_non_owner_should_return_403_forbidden(self, jwt_client_user2, collection1, user2):
        """DELETE /collections/{uid}/members/{user_uid}/ - Test removing a member by a non-owner"""
        # First, add user2 as a member of collection1
        CollectionMember.objects.create(collection=collection1, user=user2)
        
        url = reverse('collections-members-detail', kwargs={'uid': collection1.uid, 'user_uid': user2.uid})
        response = jwt_client_user2.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_remove_member_that_does_not_exist_should_return_404_not_found(self, jwt_client, collection1):
        """DELETE /collections/{uid}/members/{user_uid}/ - Test removing a non-existent member"""
        url = reverse('collections-members-detail', kwargs={'uid': collection1.uid, 'user_uid': '00000000-0000-0000-0000-000000000000'})
        response = jwt_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_remove_member_that_is_not_a_member_should_return_404_not_found(self, jwt_client, collection1, user2):
        """DELETE /collections/{uid}/members/{user_uid}/ - Test removing a user that is not a member"""
        url = reverse('collections-members-detail', kwargs={'uid': collection1.uid, 'user_uid': user2.uid})
        response = jwt_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND