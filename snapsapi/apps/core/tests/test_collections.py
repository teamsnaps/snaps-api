import pytest
from django.urls import reverse
from rest_framework import status

from snapsapi.apps.core.models import Collection


@pytest.mark.django_db
class TestCollectionListCreateView:
    """Tests for the CollectionListCreateView (/collections/)"""

    def test_list_collections_should_return_200_ok(self, jwt_client, collection1, collection_user2, collection_member, default_collection, private_collection):
        """GET /collections/ - Test listing collections"""
        url = reverse('collections-list-create')
        response = jwt_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Should return collections owned by user1 and collections where user1 is a member
        assert len(response.data['results']) == 5
        
        # Check that the response contains the expected collections
        collection_uids = [item['uid'] for item in response.data['results']]
        assert str(collection1.uid) in collection_uids
        assert str(collection_user2.uid) in collection_uids
        assert str(default_collection.uid) in collection_uids
        assert str(private_collection.uid) in collection_uids
        
    def test_get_queryset_unauthenticated_should_return_empty_queryset(self, api_client):
        """Test that get_queryset returns an empty queryset when user is not authenticated"""
        # Create a custom APIClient without authentication
        from snapsapi.apps.core.views import CollectionListCreateView
        
        # Create an instance of the view
        view = CollectionListCreateView()
        
        # Create a mock request with an unauthenticated user
        from rest_framework.test import APIRequestFactory
        from django.contrib.auth.models import AnonymousUser
        factory = APIRequestFactory()
        request = factory.get('/collections/')
        request.user = AnonymousUser()  # Proper unauthenticated user
        
        # Set the request on the view
        view.request = request
        
        # Call get_queryset
        queryset = view.get_queryset()
        
        # Verify that the queryset is empty
        assert queryset.count() == 0

    def test_list_collections_unauthenticated_should_return_401_unauthorized(self, api_client):
        """GET /collections/ - Test listing collections without authentication"""
        url = reverse('collections-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_collection_should_return_201_created(self, jwt_client):
        """POST /collections/ - Test creating a collection"""
        url = reverse('collections-list-create')
        data = {
            'name': 'New Collection',
            'description': 'A new test collection',
            'is_public': True
        }
        response = jwt_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Collection'
        assert response.data['description'] == 'A new test collection'
        assert response.data['is_public'] is True
        
        # Verify the collection was created in the database
        assert Collection.objects.filter(name='New Collection').exists()

    def test_create_collection_unauthenticated_should_return_401_unauthorized(self, api_client):
        """POST /collections/ - Test creating a collection without authentication"""
        url = reverse('collections-list-create')
        data = {
            'name': 'New Collection',
            'description': 'A new test collection',
            'is_public': True
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCollectionDetailView:
    """Tests for the CollectionDetailView (/collections/{uid}/)"""

    def test_retrieve_collection_should_return_200_ok(self, jwt_client, collection1):
        """GET /collections/{uid}/ - Test retrieving a collection"""
        url = reverse('collections-detail', kwargs={'uid': collection1.uid})
        response = jwt_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == collection1.name
        assert response.data['description'] == collection1.description
        assert response.data['is_public'] == collection1.is_public
        
    def test_destroy_collection_by_non_owner_direct_call(self, jwt_client_user2, collection1):
        """Test directly calling destroy method when collection owner is not the request user"""
        from snapsapi.apps.core.views import CollectionDetailView
        from rest_framework.test import APIRequestFactory
        
        # Create a mock request with user2
        factory = APIRequestFactory()
        request = factory.delete(f'/collections/{collection1.uid}/')
        
        # Set user2 as the request user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user2 = User.objects.get(username='user2')
        request.user = user2
        
        # Create an instance of the view
        view = CollectionDetailView()
        
        # Set the request on the view
        view.request = request
        
        # Mock the get_object method to return collection1
        original_get_object = view.get_object
        view.get_object = lambda: collection1
        
        try:
            # Call destroy method
            response = view.destroy(request)
            
            # Verify that the response is 403 Forbidden
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert response.data['detail'] == "You do not have permission to delete this collection."
        finally:
            # Restore the original get_object method
            view.get_object = original_get_object

    def test_retrieve_collection_as_member_should_return_200_ok(self, jwt_client, collection_user2, collection_member):
        """GET /collections/{uid}/ - Test retrieving a collection as a member"""
        url = reverse('collections-detail', kwargs={'uid': collection_user2.uid})
        response = jwt_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == collection_user2.name
        assert response.data['description'] == collection_user2.description
        assert response.data['is_public'] == collection_user2.is_public

    def test_retrieve_collection_unauthenticated_should_return_401_unauthorized(self, api_client, collection1):
        """GET /collections/{uid}/ - Test retrieving a collection without authentication"""
        url = reverse('collections-detail', kwargs={'uid': collection1.uid})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_collection_should_return_200_ok(self, jwt_client, collection1):
        """PATCH /collections/{uid}/ - Test updating a collection"""
        url = reverse('collections-detail', kwargs={'uid': collection1.uid})
        data = {
            'name': 'Updated Collection',
            'description': 'An updated test collection'
        }
        response = jwt_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Collection'
        assert response.data['description'] == 'An updated test collection'
        
        # Verify the collection was updated in the database
        collection1.refresh_from_db()
        assert collection1.name == 'Updated Collection'
        assert collection1.description == 'An updated test collection'

    def test_update_collection_by_non_owner_should_return_404_not_found(self, jwt_client_user2, collection1):
        """PATCH /collections/{uid}/ - Test updating a collection by a non-owner"""
        url = reverse('collections-detail', kwargs={'uid': collection1.uid})
        data = {
            'name': 'Updated Collection',
            'description': 'An updated test collection'
        }
        response = jwt_client_user2.patch(url, data, format='json')
        
        # Should return 404 because the queryset filters by owner
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_collection_should_return_204_no_content(self, jwt_client, collection1):
        """DELETE /collections/{uid}/ - Test deleting a collection"""
        url = reverse('collections-detail', kwargs={'uid': collection1.uid})
        response = jwt_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the collection was soft-deleted in the database
        collection1.refresh_from_db()
        assert collection1.is_deleted is True
        assert collection1.deleted_at is not None

    def test_delete_collection_by_non_owner_should_return_404_not_found(self, jwt_client_user2, collection1):
        """DELETE /collections/{uid}/ - Test deleting a collection by a non-owner"""
        url = reverse('collections-detail', kwargs={'uid': collection1.uid})
        response = jwt_client_user2.delete(url)
        
        # Should return 404 because the queryset filters by owner
        assert response.status_code == status.HTTP_404_NOT_FOUND