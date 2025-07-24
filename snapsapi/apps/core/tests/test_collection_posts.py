import pytest
from django.urls import reverse
from rest_framework import status

from snapsapi.apps.core.models import Collection


@pytest.mark.django_db
class TestCollectionAddPostView:
    """Tests for the CollectionAddPostView (/collections/{uid}/posts/{post_uid}/)"""

    def test_add_post_should_return_200_ok(self, jwt_client, collection1, post1):
        """POST /collections/{uid}/posts/{post_uid}/ - Test adding a post to a collection"""
        url = reverse('collections-posts-detail', kwargs={'uid': collection1.uid, 'post_uid': post1.uid})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the post was added to the collection in the database
        collection1.refresh_from_db()
        assert post1 in collection1.posts.all()

    def test_add_post_by_non_owner_should_return_403_forbidden(self, jwt_client_user2, collection1, post1):
        """POST /collections/{uid}/posts/{post_uid}/ - Test adding a post by a non-owner"""
        url = reverse('collections-posts-detail', kwargs={'uid': collection1.uid, 'post_uid': post1.uid})
        response = jwt_client_user2.post(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_add_post_that_does_not_exist_should_return_404_not_found(self, jwt_client, collection1):
        """POST /collections/{uid}/posts/{post_uid}/ - Test adding a non-existent post"""
        url = reverse('collections-posts-detail', kwargs={'uid': collection1.uid, 'post_uid': '00000000-0000-0000-0000-000000000000'})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_post_that_is_already_in_collection_should_return_400_bad_request(self, jwt_client, collection_with_post, post1):
        """POST /collections/{uid}/posts/{post_uid}/ - Test adding a post that is already in the collection"""
        url = reverse('collections-posts-detail', kwargs={'uid': collection_with_post.uid, 'post_uid': post1.uid})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_post_should_return_204_no_content(self, jwt_client, collection_with_post, post1):
        """DELETE /collections/{uid}/posts/{post_uid}/ - Test removing a post from a collection"""
        url = reverse('collections-posts-detail', kwargs={'uid': collection_with_post.uid, 'post_uid': post1.uid})
        response = jwt_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the post was removed from the collection in the database
        collection_with_post.refresh_from_db()
        assert post1 not in collection_with_post.posts.all()

    def test_remove_post_by_non_owner_should_return_403_forbidden(self, jwt_client_user2, collection_with_post, post1):
        """DELETE /collections/{uid}/posts/{post_uid}/ - Test removing a post by a non-owner"""
        url = reverse('collections-posts-detail', kwargs={'uid': collection_with_post.uid, 'post_uid': post1.uid})
        response = jwt_client_user2.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_remove_post_that_is_not_in_collection_should_return_404_not_found(self, jwt_client, collection1, post1):
        """DELETE /collections/{uid}/posts/{post_uid}/ - Test removing a post that is not in the collection"""
        url = reverse('collections-posts-detail', kwargs={'uid': collection1.uid, 'post_uid': post1.uid})
        response = jwt_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDefaultCollectionAddPostView:
    """Tests for the DefaultCollectionAddPostView (/collections/posts/{post_uid}/)"""

    def test_toggle_post_in_default_collection_add_should_return_200_ok(self, jwt_client, default_collection, post1):
        """POST /collections/posts/{post_uid}/ - Test adding a post to the default collection"""
        url = reverse('default-collection-posts-detail', kwargs={'post_uid': post1.uid})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_collected'] is True
        
        # Verify the post was added to the default collection in the database
        default_collection.refresh_from_db()
        assert post1 in default_collection.posts.all()
        
    def test_get_default_collection_exception_handling(self, monkeypatch):
        """Test the exception handling in get_default_collection method"""
        from snapsapi.apps.core.views import DefaultCollectionAddPostView
        from snapsapi.apps.core.models import Collection
        
        # Create an instance of the view
        view = DefaultCollectionAddPostView()
        
        # Create a mock user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='no_default@example.com',
            password='password',
            username='no_default'
        )
        
        # Mock the Collection.objects.filter method to raise Collection.DoesNotExist
        def mock_filter(*args, **kwargs):
            raise Collection.DoesNotExist("Test exception")
        
        # Apply the monkeypatch
        monkeypatch.setattr(Collection.objects, 'filter', mock_filter)
        
        # Call get_default_collection with the user
        result = view.get_default_collection(user)
        
        # Verify that the result is None
        assert result is None

    def test_toggle_post_in_default_collection_remove_should_return_200_ok(self, jwt_client, default_collection, post1):
        """POST /collections/posts/{post_uid}/ - Test removing a post from the default collection"""
        # First, add the post to the default collection
        default_collection.posts.add(post1)
        
        url = reverse('default-collection-posts-detail', kwargs={'post_uid': post1.uid})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_collected'] is False
        
        # Verify the post was removed from the default collection in the database
        default_collection.refresh_from_db()
        assert post1 not in default_collection.posts.all()

    def test_toggle_post_in_default_collection_unauthenticated_should_return_401_unauthorized(self, api_client, post1):
        """POST /collections/posts/{post_uid}/ - Test toggling a post without authentication"""
        url = reverse('default-collection-posts-detail', kwargs={'post_uid': post1.uid})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_toggle_post_that_does_not_exist_should_return_404_not_found(self, jwt_client, default_collection):
        """POST /collections/posts/{post_uid}/ - Test toggling a non-existent post"""
        url = reverse('default-collection-posts-detail', kwargs={'post_uid': '00000000-0000-0000-0000-000000000000'})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_toggle_post_without_default_collection_should_return_404_not_found(self, jwt_client, user1, post1):
        """POST /collections/posts/{post_uid}/ - Test toggling a post without a default collection"""
        # Delete the default collection if it exists
        Collection.objects.filter(owner=user1, name='default').delete()
        
        url = reverse('default-collection-posts-detail', kwargs={'post_uid': post1.uid})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND