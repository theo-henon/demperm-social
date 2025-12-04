import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.exceptions import PermissionDenied
from common.exceptions import NotFoundError, PermissionDeniedError, ConflictError
from apps.posts.views import CreatePostView
from apps.posts.views import PostDetailView
from apps.posts.views import DeletePostView
from apps.posts.views import LikePostView
from apps.posts.views import UnlikePostView
from apps.posts.views import PostLikesView
from apps.posts.views import FeedView
from apps.posts.views import DiscoverView
from services.apps_services.post_service import PostService

from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime
import uuid
from django.db import models
from django.core.validators import RegexValidator
from db.entities.post_entity import Post, Like
from common.exceptions import NotFoundError, ValidationError, PermissionDeniedError, ConflictError







class TestPostViews(APITestCase):
    """Test suite for Post API views."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        self.post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        self.subforum_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

        # Mock authenticated user
        self.user = Mock()
        self.user.user_id = self.user_id
        self.user.is_authenticated = True

    @patch('services.apps_services.post_service.PostService.create_post')
    @patch('common.utils.get_client_ip')
    def test_create_post_success(self, mock_get_ip, mock_create_post):
        """Test successful post creation via API."""
        self.client.force_authenticate(user=self.user)
        mock_get_ip.return_value = "127.0.0.1"

        mock_post = Mock()
        mock_post.post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        mock_post.author_id = self.user_id
        mock_post.subforum_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        mock_post.title = "Test Post"
        mock_post.content = "Test content"
        mock_post.content_signature = "sig123"
        mock_post.like_count = 0
        mock_post.comment_count = 0
        mock_post.created_at = datetime.now()
        mock_post.updated_at = datetime.now()
        mock_create_post.return_value = mock_post

        data = {
            'title': 'Test Post',
            'content': 'Test content',
            'subforum_id': str(self.subforum_id)
        }

        response = self.client.post('/api/posts/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('post_id', response.data)
        self.assertEqual(response.data['title'], 'Test Post')

    def test_create_post_unauthenticated(self):
        """Test post creation fails without authentication."""
        data = {
            'title': 'Test Post',
            'content': 'Test content',
            'subforum_id': str(self.subforum_id)
        }

        response = self.client.post('/api/posts/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('services.apps_services.post_service.PostService.create_post')
    def test_create_post_validation_error(self, mock_create_post):
        """Test post creation with validation error."""
        self.client.force_authenticate(user=self.user)
        mock_create_post.side_effect = ValidationError("Title is required")

        data = {
            'title': '',
            'content': 'Test content',
            'subforum_id': str(self.subforum_id)
        }

        response = self.client.post('/api/posts/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('services.apps_services.post_service.PostService.get_post_by_id')
    def test_get_post_detail_success(self, mock_get_post):
        """Test successful post retrieval."""
        self.client.force_authenticate(user=self.user)

        mock_post = Mock()
        mock_post.post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        mock_post.author_id = self.user_id
        mock_post.author.username = "testuser"
        mock_post.subforum_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        mock_post.title = "Test Post"
        mock_post.content = "Test content"
        mock_post.content_signature = "sig123"
        mock_post.like_count = 5
        mock_post.comment_count = 3
        mock_post.created_at = datetime.now()
        mock_post.updated_at = datetime.now()
        mock_get_post.return_value = mock_post

        response = self.client.get(f'/api/posts/{self.post_id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')
        self.assertEqual(response.data['author_username'], 'testuser')

    @patch('services.apps_services.post_service.PostService.get_post_by_id')
    def test_get_post_detail_not_found(self, mock_get_post):
        """Test post retrieval for non-existent post."""
        self.client.force_authenticate(user=self.user)
        mock_get_post.side_effect = NotFoundError("Post not found")

        response = self.client.get(f'/api/posts/{self.post_id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('services.apps_services.post_service.PostService.get_post_by_id')
    def test_get_post_detail_permission_denied(self, mock_get_post):
        """Test post retrieval with permission denied."""
        self.client.force_authenticate(user=self.user)
        mock_get_post.side_effect = PermissionDeniedError("Cannot view private post")

        response = self.client.get(f'/api/posts/{self.post_id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('services.apps_services.post_service.PostService.delete_post')
    @patch('common.utils.get_client_ip')
    def test_delete_post_success(self, mock_get_ip, mock_delete_post):
        """Test successful post deletion."""
        self.client.force_authenticate(user=self.user)
        mock_get_ip.return_value = "127.0.0.1"
        mock_delete_post.return_value = None

        response = self.client.delete(f'/api/posts/{self.post_id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete_post.assert_called_once()

    @patch('services.apps_services.post_service.PostService.delete_post')
    @patch('common.utils.get_client_ip')
    def test_delete_post_not_found(self, mock_get_ip, mock_delete_post):
        """Test deleting non-existent post."""
        self.client.force_authenticate(user=self.user)
        mock_get_ip.return_value = "127.0.0.1"
        mock_delete_post.side_effect = NotFoundError("Post not found")

        response = self.client.delete(f'/api/posts/{self.post_id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('services.apps_services.post_service.PostService.like_post')
    @patch('common.utils.get_client_ip')
    def test_like_post_success(self, mock_get_ip, mock_like_post):
        """Test successful post like."""
        self.client.force_authenticate(user=self.user)
        mock_get_ip.return_value = "127.0.0.1"

        mock_like = Mock()
        mock_like.like_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        mock_like.user_id = self.user_id
        mock_like.post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        mock_like.created_at = datetime.now()
        mock_like_post.return_value = mock_like

        response = self.client.post(f'/api/posts/{self.post_id}/like/')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('like_id', response.data)

    @patch('services.apps_services.post_service.PostService.unlike_post')
    @patch('common.utils.get_client_ip')
    def test_unlike_post_success(self, mock_get_ip, mock_unlike_post):
        """Test successful post unlike."""
        self.client.force_authenticate(user=self.user)
        mock_get_ip.return_value = "127.0.0.1"
        mock_unlike_post.return_value = None

        response = self.client.delete(f'/api/posts/{self.post_id}/unlike/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes(self, mock_get_likes):
        """Test getting post likes."""
        self.client.force_authenticate(user=self.user)

        mock_likes = []
        for i in range(3):
            mock_like = Mock()
            mock_like.like_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
            mock_like.user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
            mock_like.user.username = f"user{i}"
            mock_like.post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
            mock_like.created_at = datetime.now()
            mock_likes.append(mock_like)

        mock_get_likes.return_value = mock_likes

        response = self.client.get(f'/api/posts/{self.post_id}/likes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    @patch('services.apps_services.post_service.PostService.get_feed')
    def test_get_feed(self, mock_get_feed):
        """Test getting personalized feed."""
        self.client.force_authenticate(user=self.user)

        mock_posts = []
        for i in range(3):
            mock_post = Mock()
            mock_post.post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
            mock_post.author_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
            mock_post.author.username = f"author{i}"
            mock_post.subforum_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
            mock_post.title = f"Post {i}"
            mock_post.content = f"Content {i}"
            mock_post.like_count = i
            mock_post.comment_count = i
            mock_post.created_at = datetime.now()
            mock_posts.append(mock_post)

        mock_get_feed.return_value = mock_posts

        response = self.client.get('/api/feed/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    @patch('services.apps_services.post_service.PostService.get_discover')
    def test_get_discover(self, mock_get_discover):
        """Test getting discover feed."""
        self.client.force_authenticate(user=self.user)

        mock_posts = []
        for i in range(3):
            mock_post = Mock()
            mock_post.post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
            mock_post.author_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
            mock_post.author.username = f"author{i}"
            mock_post.subforum_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
            mock_post.title = f"Trending Post {i}"
            mock_post.content = f"Trending content {i}"
            mock_post.like_count = 100 + i
            mock_post.comment_count = 50 + i
            mock_post.created_at = datetime.now()
            mock_posts.append(mock_post)

        mock_get_discover.return_value = mock_posts

        response = self.client.get('/api/discover/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    @patch('services.apps_services.post_service.PostService.get_feed')
    def test_get_feed_with_pagination(self, mock_get_feed):
        """Test feed with pagination parameters."""
        self.client.force_authenticate(user=self.user)
        mock_get_feed.return_value = []

        response = self.client.get('/api/feed/?page=2&page_size=10')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_feed.assert_called_once_with(str(self.user_id), 2, 10)

    @patch('services.apps_services.post_service.PostService.get_discover')
    def test_get_discover_with_pagination(self, mock_get_discover):
        """Test discover feed with pagination parameters."""
        self.client.force_authenticate(user=self.user)
        mock_get_discover.return_value = []

        response = self.client.get('/api/discover/?page=3&page_size=15')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_discover.assert_called_once_with(str(self.user_id), 3, 15)