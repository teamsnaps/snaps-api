import pytest
from django.urls import reverse
from rest_framework import status

from snapsapi.apps.likes.models import PostLike, CommentLike


@pytest.mark.django_db
class TestPostLikeToggleView:
    """Tests for the PostLikeToggleView (/api/posts/{uid}/like/)"""

    def test_toggle_post_like_create_should_return_200_ok(self, jwt_client, post1):
        """POST /api/posts/{uid}/like/ - Test creating a like on a post"""
        url = reverse('posts:like-toggle', kwargs={'uid': post1.uid})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['likes_count'] == 1
        assert response.data['is_liked'] is True
        
        # Verify the like was created in the database
        assert PostLike.objects.filter(post=post1).count() == 1

    def test_toggle_post_like_delete_should_return_200_ok(self, jwt_client, post1, post_like):
        """POST /api/posts/{uid}/like/ - Test removing a like from a post"""
        url = reverse('posts:like-toggle', kwargs={'uid': post1.uid})
        response = jwt_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['likes_count'] == 0
        assert response.data['is_liked'] is False
        
        # Verify the like was deleted from the database
        assert PostLike.objects.filter(post=post1).count() == 0

    def test_toggle_post_like_unauthenticated_should_return_401_unauthorized(self, api_client, post1):
        """POST /api/posts/{uid}/like/ - Test liking a post without authentication"""
        url = reverse('posts:like-toggle', kwargs={'uid': post1.uid})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# @pytest.mark.django_db
# class TestCommentLikeToggleView:
#     """Tests for the CommentLikeToggleView (/api/comments/{uid}/like/)"""
#
#     def test_toggle_comment_like_create_should_return_200_ok(self, jwt_client, comment1):
#         """POST /api/comments/{uid}/like/ - Test creating a like on a comment"""
#         url = reverse('likes:comment-like-toggle', kwargs={'uid': comment1.uid})
#         response = jwt_client.post(url)
#
#         assert response.status_code == status.HTTP_200_OK
#         assert response.data['likes_count'] == 1
#         assert response.data['is_liked'] is True
#
#         # Verify the like was created in the database
#         assert CommentLike.objects.filter(comment=comment1).count() == 1
#
#     def test_toggle_comment_like_delete_should_return_200_ok(self, jwt_client, comment1, comment_like):
#         """POST /api/comments/{uid}/like/ - Test removing a like from a comment"""
#         url = reverse('likes:comment-like-toggle', kwargs={'uid': comment1.uid})
#         response = jwt_client.post(url)
#
#         assert response.status_code == status.HTTP_200_OK
#         assert response.data['likes_count'] == 0
#         assert response.data['is_liked'] is False
#
#         # Verify the like was deleted from the database
#         assert CommentLike.objects.filter(comment=comment1).count() == 0
#
#     def test_toggle_comment_like_unauthenticated_should_return_401_unauthorized(self, api_client, comment1):
#         """POST /api/comments/{uid}/like/ - Test liking a comment without authentication"""
#         url = reverse('likes:comment-like-toggle', kwargs={'uid': comment1.uid})
#         response = api_client.post(url)
#
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
#
#     def test_like_count_increments_correctly(self, jwt_client, comment1):
#         """Test that the likes_count field is incremented correctly when a like is created"""
#         # Initial likes count should be 0
#         assert comment1.likes_count == 0
#
#         # Create a like
#         url = reverse('likes:comment-like-toggle', kwargs={'uid': comment1.uid})
#         jwt_client.post(url)
#
#         # Refresh the comment from the database
#         comment1.refresh_from_db()
#
#         # Likes count should be 1
#         assert comment1.likes_count == 1
#
#     def test_like_count_decrements_correctly(self, jwt_client, comment1, comment_like):
#         """Test that the likes_count field is decremented correctly when a like is deleted"""
#         # Initial likes count should be 1 because of the comment_like fixture
#         comment1.refresh_from_db()
#         assert comment1.likes_count == 1
#
#         # Delete the like
#         url = reverse('likes:comment-like-toggle', kwargs={'uid': comment1.uid})
#         jwt_client.post(url)
#
#         # Refresh the comment from the database
#         comment1.refresh_from_db()
#
#         # Likes count should be 0
#         assert comment1.likes_count == 0