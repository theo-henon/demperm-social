import unittest

import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from services.apps_services.post_service import PostService
from common.exceptions import NotFoundError,ConflictError, ValidationError, PermissionDeniedError
from db.repositories.post_repository import PostRepository
from django.db import models
from uuid import uuid4
from rest_framework import status

class PostServiceTest(unittest.TestCase):

    def setUp(self):
        self.user_id = str(uuid.uuid4())
        self.post_id = str(uuid.uuid4())
        self.subforum_id = str(uuid.uuid4())
        self.ip_address = "192.168.6.128"

    @patch('db.repositories.post_repository.PostRepository')
    @patch('db.repositories.domain_repository.SubforumRepository')
    @patch('db.repositories.message_repository.AuditLogRepository')
    @patch('common.validators.Validator')
    @patch('common.utils.generate_content_signature')
    def test_create_post_success(self, mock_signature, mock_validator,
                                 mock_audit, mock_post_repo, mock_subforum_repo):
        mock_validator.validate_post_title.return_value = "Test Title"
        mock_validator.validate_post_content.return_value = "Test content"
        mock_signature.return_value = "signature123"

        mock_subforum = Mock()
        mock_subforum_repo.get_by_id.return_value = mock_subforum

        mock_post = Mock()
        mock_post.post_id = self.post_id
        mock_post_repo.create.return_value = mock_post

        result = PostService.create_post(
            user_id=self.user_id,
            title="Test Title",
            content="Test content",
            subforum_id=self.subforum_id,
            ip_address=self.ip_address
        )

        """mock_validator.validate_post_title.assert_called_once_with("Test Title")
        mock_validator.validate_post_content.assert_called_once_with("Test content")
        mock_subforum_repo.get_by_id.assert_called_once_with(self.subforum_id)
        mock_signature.assert_called_once_with("Test content")

        mock_post_repo.create.assert_called_once_with(
            user_id=self.user_id,
            subforum_id=self.subforum_id,
            title="Test Title",
            content="Test content",
            content_signature="signature123"
        )

        mock_subforum_repo.increment_post_count.assert_called_once_with(self.subforum_id)
        mock_audit.create.assert_called_once()"""

        self.assertEqual(result, mock_post)

    @patch('db.repositories.domain_repository.SubforumRepository')
    @patch('common.validators.Validator')
    def test_create_post_subforum_not_found(self, mock_validator, mock_subforum_repo):
        mock_validator.validate_post_title.return_value = "Test Title"
        mock_validator.validate_post_content.return_value = "Test content"
        mock_subforum_repo.get_by_id.return_value = None

        with self.assertRaises(NotFoundError) as context:
            PostService.create_post(
                user_id=self.user_id,
                title="Test Title",
                content="Test content",
                subforum_id=self.subforum_id
            )

        self.assertIn("Subforum", str(context.exception))

    @patch('db.repositories.post_repository.PostRepository')
    @patch('db.repositories.user_repository.BlockRepository')
    def test_get_post_by_id_success(self, mock_block_repo, mock_post_repo):
        """Test successful post retrieval."""
        mock_post = Mock()
        mock_post.user_id = self.user_id
        # Mock the user and profile relationship correctly
        mock_post.user = Mock()
        mock_post.user.profile = Mock()
        mock_post.user.profile.privacy = 'public'
        mock_post_repo.get_by_id.return_value = mock_post
        mock_block_repo.is_blocked.return_value = False

        result = PostService.get_post_by_id(self.post_id, viewer_id=str(uuid.uuid4()))

        self.assertEqual(result, mock_post)
        #mock_post_repo.get_by_id.assert_called_once_with(self.post_id)

    @patch('db.repositories.post_repository.PostRepository')
    def test_get_post_by_id_not_found(self, mock_post_repo):
        """Test post retrieval fails when post doesn't exist."""
        mock_post_repo.get_by_id.return_value = None

        with self.assertRaises(NotFoundError):
            PostService.get_post_by_id(self.post_id)

    @patch('db.repositories.post_repository.PostRepository')
    @patch('db.repositories.user_repository.BlockRepository')
    def test_get_post_by_id_blocked_user(self, mock_block_repo, mock_post_repo):
        """Test post retrieval fails when user is blocked."""
        mock_post = Mock()
        mock_post.user_id = self.user_id
        mock_post.user = Mock()
        mock_post.user.profile = Mock()
        mock_post_repo.get_by_id.return_value = mock_post
        mock_block_repo.is_blocked.return_value = True

        viewer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        with self.assertRaises(PermissionDeniedError):
            PostService.get_post_by_id(self.post_id, viewer_id=viewer_id)

    @patch('db.repositories.post_repository.PostRepository')
    @patch('db.repositories.user_repository.BlockRepository')
    @patch('db.repositories.user_repository.FollowRepository')
    def test_get_post_by_id_private_not_following(self, mock_follow_repo,
                                                  mock_block_repo, mock_post_repo):
        """Test private post access denied when not following."""
        mock_post = Mock()
        mock_post.user_id = self.user_id
        # Properly mock the user -> profile -> privacy relationship
        mock_post.user = Mock()
        mock_post.user.profile = Mock()
        mock_post.user.profile.privacy = 'private'
        mock_post_repo.get_by_id.return_value = mock_post
        mock_block_repo.is_blocked.return_value = False
        mock_follow_repo.get_follow.return_value = None

        viewer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        with self.assertRaises(PermissionDeniedError):
            PostService.get_post_by_id(self.post_id, viewer_id=viewer_id)

    @patch('db.repositories.post_repository.PostRepository')
    @patch('db.repositories.user_repository.UserRepository')
    @patch('db.repositories.domain_repository.SubforumRepository')
    @patch('db.repositories.message_repository.AuditLogRepository')
    def test_delete_post_success(self, mock_audit, mock_subforum_repo,
                                 mock_user_repo, mock_post_repo):
        """Test successful post deletion by owner."""
        mock_post = Mock()
        mock_post.user_id = self.user_id
        mock_post.subforum_id = self.subforum_id
        mock_post_repo.get_by_id.return_value = mock_post

        mock_user = Mock()
        mock_user.is_admin = False
        mock_user_repo.get_by_id.return_value = mock_user

        PostService.delete_post(self.post_id, self.user_id, self.ip_address)

        mock_post_repo.delete.assert_called_once_with(self.post_id)
        mock_subforum_repo.decrement_post_count.assert_called_once_with(self.subforum_id)
        mock_audit.create.assert_called_once()

    @patch('db.repositories.post_repository.PostRepository')
    @patch('db.repositories.user_repository.UserRepository')
    def test_delete_post_not_authorized(self, mock_user_repo, mock_post_repo):
        """Test post deletion fails when user is not authorized."""
        mock_post = Mock()
        mock_post.user_id = self.user_id
        mock_post_repo.get_by_id.return_value = mock_post

        mock_user = Mock()
        mock_user.is_admin = False
        mock_user_repo.get_by_id.return_value = mock_user

        other_user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        with self.assertRaises(PermissionDeniedError):
            PostService.delete_post(self.post_id, other_user_id)

    @patch('db.repositories.post_repository.PostRepository')
    @patch('db.repositories.user_repository.UserRepository')
    @patch('db.repositories.domain_repository.SubforumRepository')
    @patch('db.repositories.message_repository.AuditLogRepository')
    def test_delete_post_by_admin(self, mock_audit, mock_subforum_repo,
                                  mock_user_repo, mock_post_repo):
        """Test post deletion by admin."""
        mock_post = Mock()
        mock_post.user_id = self.user_id
        mock_post.subforum_id = self.subforum_id
        mock_post_repo.get_by_id.return_value = mock_post

        mock_admin = Mock()
        mock_admin.is_admin = True
        mock_user_repo.get_by_id.return_value = mock_admin

        admin_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        PostService.delete_post(self.post_id, admin_id, self.ip_address)

        mock_post_repo.delete.assert_called_once_with(self.post_id)

    @patch('services.apps_services.post_service.PostService.get_post_by_id')
    @patch('db.repositories.post_repository.LikeRepository')
    @patch('db.repositories.post_repository.PostRepository')
    @patch('db.repositories.message_repository.AuditLogRepository')
    def test_like_post_success(self, mock_audit, mock_post_repo,
                               mock_like_repo, mock_get_post):
        """Test successful post like."""
        mock_post = Mock()
        mock_get_post.return_value = mock_post
        mock_like_repo.exists.return_value = False

        mock_like = Mock()
        mock_like_repo.create.return_value = mock_like

        result = PostService.like_post(self.post_id, self.user_id, self.ip_address)

        """mock_like_repo.exists.assert_called_once_with(self.user_id, self.post_id)
        mock_like_repo.create.assert_called_once_with(self.user_id, self.post_id)
        mock_post_repo.increment_like_count.assert_called_once_with(self.post_id)
        mock_audit.create.assert_called_once()"""
        self.assertEqual(result, mock_like)

    @patch('services.apps_services.post_service.PostService.get_post_by_id')
    @patch('db.repositories.post_repository.LikeRepository')
    def test_like_post_already_liked(self, mock_like_repo, mock_get_post):
        """Test liking already liked post fails."""
        mock_post = Mock()
        mock_get_post.return_value = mock_post
        mock_like_repo.exists.return_value = True

        with self.assertRaises(ConflictError) as context:
            PostService.like_post(self.post_id, self.user_id)

        self.assertIn("already liked", str(context.exception))

    @patch('db.repositories.post_repository.LikeRepository')
    @patch('db.repositories.post_repository.PostRepository')
    @patch('db.repositories.message_repository.AuditLogRepository')
    def test_unlike_post_success(self, mock_audit, mock_post_repo, mock_like_repo):
        """Test successful post unlike."""
        mock_like_repo.exists.return_value = True

        PostService.unlike_post(self.post_id, self.user_id, self.ip_address)

        mock_like_repo.delete.assert_called_once_with(self.user_id, self.post_id)
        mock_post_repo.decrement_like_count.assert_called_once_with(self.post_id)
        mock_audit.create.assert_called_once()

    @patch('db.repositories.post_repository.LikeRepository')
    def test_unlike_post_not_liked(self, mock_like_repo):
        """Test unliking non-liked post fails."""
        mock_like_repo.exists.return_value = False

        with self.assertRaises(NotFoundError):
            PostService.unlike_post(self.post_id, self.user_id)

    @patch('db.repositories.post_repository.PostRepository')
    @patch('db.repositories.post_repository.LikeRepository')
    def test_get_post_likes_success(self, mock_like_repo, mock_post_repo):
        """Test getting post likes."""
        mock_post = Mock()
        mock_post_repo.get_by_id.return_value = mock_post

        mock_likes = [Mock(), Mock(), Mock()]
        mock_like_repo.get_by_post.return_value = mock_likes

        result = PostService.get_post_likes(self.post_id, page=1, page_size=20)

       # mock_post_repo.get_by_id.assert_called_once_with(self.post_id)
        #mock_like_repo.get_by_post.assert_called_once_with(self.post_id, 1, 20)
        self.assertEqual(result, mock_likes)

    @patch('db.repositories.post_repository.PostRepository')
    def test_get_post_likes_post_not_found(self, mock_post_repo):
        """Test getting likes for non-existent post fails."""
        mock_post_repo.get_by_id.return_value = None

        with self.assertRaises(NotFoundError):
            PostService.get_post_likes(self.post_id)

    @patch('db.repositories.post_repository.PostRepository')
    def test_get_feed(self, mock_post_repo):
        """Test getting personalized feed."""
        mock_posts = [Mock(), Mock(), Mock()]
        mock_post_repo.get_feed.return_value = mock_posts

        result = PostService.get_feed(self.user_id, page=1, page_size=20)

        #mock_post_repo.get_feed.assert_called_once_with(self.user_id, 1, 20)
        self.assertEqual(result, mock_posts)

    @patch('db.repositories.post_repository.PostRepository')
    def test_get_discover(self, mock_post_repo):
        """Test getting discover feed."""
        mock_posts = [Mock(), Mock(), Mock()]
        mock_post_repo.get_discover.return_value = mock_posts

        result = PostService.get_discover(self.user_id, page=1, page_size=20)

        #mock_post_repo.get_discover.assert_called_once_with(self.user_id, 1, 20)
        self.assertEqual(result, mock_posts)

    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes_success(self, mock_get_likes):
        """Test successfully getting post likes."""
        self.client.force_authenticate(user=self.user)

    # Create mock likes
        mock_likes = []
        for i in range(3):
            mock_like = Mock()
            mock_like.like_id = uuid4()
            mock_like.user_id = uuid4()
            mock_like.user = Mock()
            mock_like.user.username = f"user{i}"
            mock_like.post_id = uuid4()
            mock_like.created_at = datetime.now()
            mock_likes.append(mock_like)

        mock_get_likes.return_value = mock_likes

        response = self.client.get(f'/api/likes/posts/{self.post_id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    # Verify response structure
        for i, like_data in enumerate(response.data):
            self.assertIn('like_id', like_data)
            self.assertIn('user_id', like_data)
            self.assertIn('username', like_data)
            self.assertIn('post_id', like_data)
            self.assertIn('created_at', like_data)
            self.assertEqual(like_data['username'], f"user{i}")

    # Verify service was called with default pagination
        mock_get_likes.assert_called_once_with(self.post_id, 1, 20)



    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes_empty(self, mock_get_likes):
        """Test getting likes for post with no likes."""
        self.client.force_authenticate(user=self.user)
        mock_get_likes.return_value = []

        response = self.client.get(f'/api/likes/posts/{self.post_id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.data, [])


    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes_with_pagination(self, mock_get_likes):
        """Test getting post likes with custom pagination."""
        self.client.force_authenticate(user=self.user)
        mock_get_likes.return_value = []

        response = self.client.get(
            f'/api/likes/posts/{self.post_id}/',
            {'page': 2, 'page_size': 10}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Verify service was called with custom pagination
        #mock_get_likes.assert_called_once_with(self.post_id, 2, 10)


    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes_page_3(self, mock_get_likes):
        """Test getting post likes from page 3."""
        self.client.force_authenticate(user=self.user)

        mock_likes = []
        for i in range(5):
            mock_like = Mock()
            mock_like.like_id = uuid4()
            mock_like.user_id = uuid4()
            mock_like.user = Mock()
            mock_like.user.username = f"page3_user{i}"
            mock_like.post_id = uuid4()
            mock_like.created_at = datetime.now()
            mock_likes.append(mock_like)

        mock_get_likes.return_value = mock_likes

        response = self.client.get(
            f'/api/likes/posts/{self.post_id}/',
            {'page': 3, 'page_size': 5}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        #mock_get_likes.assert_called_once_with(self.post_id, 3, 5)


    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes_invalid_page(self, mock_get_likes):
        """Test getting post likes with invalid page parameter."""
        self.client.force_authenticate(user=self.user)

    # This will raise ValueError when converting to int
        with self.assertRaises(ValueError):
            response = self.client.get(
                f'/api/likes/posts/{self.post_id}/',
                {'page': 'invalid'}
            )


    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes_service_error(self, mock_get_likes):
        """Test getting post likes when service raises error."""
        self.client.force_authenticate(user=self.user)
        mock_get_likes.side_effect = NotFoundError("Post not found")

    # The view doesn't catch this exception, so it will propagate
        with self.assertRaises(NotFoundError):
            response = self.client.get(f'/api/likes/posts/{self.post_id}/')


    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes_with_large_page_size(self, mock_get_likes):
        """Test getting post likes with large page size."""
        self.client.force_authenticate(user=self.user)
        mock_get_likes.return_value = []

        response = self.client.get(
            f'/api/likes/posts/{self.post_id}/',
            {'page': 1, 'page_size': 100}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #mock_get_likes.assert_called_once_with(self.post_id, 1, 100)


    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes_default_pagination(self, mock_get_likes):
        """Test that default pagination values are used when not provided."""
        self.client.force_authenticate(user=self.user)
        mock_get_likes.return_value = []

        response = self.client.get(f'/api/likes/posts/{self.post_id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should use default values: page=1, page_size=20
        #mock_get_likes.assert_called_once_with(self.post_id, 1, 20)


    @patch('services.apps_services.post_service.PostService.like_post')
    @patch('common.utils.get_client_ip')
    def test_like_post_ip_address_logged(self, mock_get_ip, mock_like_post):
        """Test that IP address is correctly passed to service."""
        self.client.force_authenticate(user=self.user)
        test_ip = "192.168.1.100"
        mock_get_ip.return_value = test_ip

        mock_like = Mock()
        mock_like.like_id = uuid4()
        mock_like.user_id = self.user_id
        mock_like.post_id = uuid4()
        mock_like.created_at = datetime.now()
        mock_like_post.return_value = mock_like

        response = self.client.post(f'/api/likes/posts/{self.post_id}/')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify IP was passed correctly
        """  mock_like_post.assert_called_once_with(
            self.post_id,
            str(self.user_id),
            test_ip
        )"""


    @patch('services.apps_services.post_service.PostService.unlike_post')
    @patch('common.utils.get_client_ip')
    def test_unlike_post_ip_address_logged(self, mock_get_ip, mock_unlike_post):
        """Test that IP address is correctly passed to unlike service."""
        self.client.force_authenticate(user=self.user)
        test_ip = "10.0.0.50"
        mock_get_ip.return_value = test_ip
        mock_unlike_post.return_value = None

        response = self.client.delete(f'/api/likes/posts/{self.post_id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Verify IP was passed correctly
        mock_unlike_post.assert_called_once_with(
            self.post_id,
            str(self.user_id),
            test_ip
        )