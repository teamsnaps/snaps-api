import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from .payloads import (
    CREATE_COMMENT_PAYLOAD,
    CREATE_REPLY_PAYLOAD,
    UPDATE_COMMENT_PAYLOAD
)


@pytest.mark.django_db
class TestCommentListCreateView:
    """Tests for the CommentListCreateView (/api/posts/{uid}/comments/)"""

    def test_list_comments_should_return_200_ok(self, api_client, post1, comment1, reply1):
        """GET /api/posts/{uid}/comments/ - Test retrieving comments for a post"""
        url = reverse('posts:comments-list-create', kwargs={'uid': post1.uid})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1  # At least one comment should be returned
        assert response.data[0]['content'] == comment1.content
        
        # Check that replies are included
        assert len(response.data[0]['replies']) >= 1
        assert response.data[0]['replies'][0]['content'] == reply1.content

    def test_create_comment_should_return_201_created(self, jwt_client, post1):
        """POST /api/posts/{uid}/comments/ - Test creating a comment on a post"""
        url = reverse('posts:comments-list-create', kwargs={'uid': post1.uid})
        response = jwt_client.post(url, CREATE_COMMENT_PAYLOAD, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == CREATE_COMMENT_PAYLOAD['content']
        assert response.data['parent'] is None  # Should be a top-level comment

    def test_create_reply_should_return_201_created(self, jwt_client, post1, comment1):
        """POST /api/posts/{uid}/comments/ - Test creating a reply to a comment"""
        url = reverse('posts:comments-list-create', kwargs={'uid': post1.uid})
        
        # Set the parent_uid dynamically
        payload = CREATE_REPLY_PAYLOAD.copy()
        payload['parent_uid'] = str(comment1.uid)
        
        response = jwt_client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == payload['content']
        assert response.data['parent'] == comment1.uid  # Should reference the parent comment

    def test_create_comment_on_deleted_post_should_return_403_forbidden(self, jwt_client, user1):
        """POST /api/posts/{uid}/comments/ - Test creating a comment on a deleted post"""
        # Create a deleted post
        from snapsapi.apps.posts.models import Post
        deleted_post = Post.objects.create(
            user=user1,
            caption="deleted post",
            is_deleted=True,
            is_active=False,
        )
        
        url = reverse('posts:comments-list-create', kwargs={'uid': deleted_post.uid})
        response = jwt_client.post(url, CREATE_COMMENT_PAYLOAD, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_comment_unauthenticated_should_return_401_unauthorized(self, api_client, post1):
        """POST /api/posts/{uid}/comments/ - Test creating a comment without authentication"""
        url = reverse('posts:comments-list-create', kwargs={'uid': post1.uid})
        response = api_client.post(url, CREATE_COMMENT_PAYLOAD, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('snapsapi.apps.notifications.services.FCMService.send_notifications_to_user')
    def test_create_comment_should_send_notification_to_post_owner(self, mock_send_notifications, jwt_client_user2, post1, user1):
        """POST /api/posts/{uid}/comments/ - Test that a notification is sent to the post owner when a comment is created"""
        url = reverse('posts:comments-list-create', kwargs={'uid': post1.uid})
        response = jwt_client_user2.post(url, CREATE_COMMENT_PAYLOAD, format='json')
        
        # Verify the comment was created successfully
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify that send_notifications_to_user was called with the correct parameters
        mock_send_notifications.assert_called_once()
        
        # Check the first argument (user_id)
        args, kwargs = mock_send_notifications.call_args
        assert kwargs['user_id'] == user1.id
        
        # Check that title and body are present
        assert 'title' in kwargs
        assert 'body' in kwargs
        
        # Check that data contains the required fields
        assert 'data' in kwargs
        assert 'post_id' in kwargs['data']
        assert 'comment_id' in kwargs['data']
        assert 'type' in kwargs['data']
        assert kwargs['data']['type'] == 'new_comment'
        
    @patch('snapsapi.apps.notifications.services.FCMService.send_notifications_to_user')
    def test_create_comment_on_own_post_should_not_send_notification(self, mock_send_notifications, jwt_client, post1):
        """POST /api/posts/{uid}/comments/ - Test that no notification is sent when a user comments on their own post"""
        url = reverse('posts:comments-list-create', kwargs={'uid': post1.uid})
        response = jwt_client.post(url, CREATE_COMMENT_PAYLOAD, format='json')
        
        # Verify the comment was created successfully
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify that send_notifications_to_user was not called
        mock_send_notifications.assert_not_called()


@pytest.mark.django_db
class TestCommentDetailView:
    """Tests for the CommentDetailView (/api/comments/{uid}/)"""

    def test_update_comment_should_return_200_ok(self, jwt_client, comment1):
        """PATCH /api/comments/{uid}/ - Test updating a comment"""
        url = reverse('comments:comments-detail', kwargs={'uid': comment1.uid})
        response = jwt_client.patch(url, UPDATE_COMMENT_PAYLOAD, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == UPDATE_COMMENT_PAYLOAD['content']

    def test_update_comment_by_different_user_should_return_403_forbidden(self, jwt_client_user2, comment1):
        """PATCH /api/comments/{uid}/ - Test updating a comment by a different user"""
        url = reverse('comments:comments-detail', kwargs={'uid': comment1.uid})
        response = jwt_client_user2.patch(url, UPDATE_COMMENT_PAYLOAD, format='json')
        
        # This should fail because the comment belongs to user1, not user2
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_comment_should_return_204_no_content(self, jwt_client, comment1):
        """DELETE /api/comments/{uid}/ - Test deleting a comment"""
        url = reverse('comments:comments-detail', kwargs={'uid': comment1.uid})
        response = jwt_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the comment was soft-deleted
        comment1.refresh_from_db()
        assert comment1.is_deleted is True

    def test_delete_comment_by_different_user_should_return_403_forbidden(self, jwt_client_user2, comment1):
        """DELETE /api/comments/{uid}/ - Test deleting a comment by a different user"""
        url = reverse('comments:comments-detail', kwargs={'uid': comment1.uid})
        response = jwt_client_user2.delete(url)
        
        # This should fail because the comment belongs to user1, not user2
        assert response.status_code == status.HTTP_403_FORBIDDEN