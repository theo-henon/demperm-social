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
from db.entities.domain_entity import Subforum, Domain, Forum
from db.entities.user_entity import User
from db.entities.post_entity import Post, Like
from db.repositories.post_repository import PostRepository, CommentRepository
from db.repositories.user_repository import UserRepository, BlockRepository, FollowRepository
from db.repositories.domain_repository import SubforumRepository
from services.apps_services.user_service import UserService

class PostServiceTest(unittest.TestCase):

    def setUp(self):
        # Create users
        # Create user
        self.user = UserRepository.create(
            google_id= str(uuid.uuid4()),
            email="user@gmail.com",
            username="alice",

        )

        # Create viewer user (for permission tests)
        self.viewer = UserRepository.create(
            google_id=str(uuid.uuid4()),
            email="viewer@gmail.com",
            username="bob",
        )

        self.blocked = UserRepository.create(
            google_id=str(uuid.uuid4()),
            email="hank@gmail.com",
            username="hank",
        )

        self.block = BlockRepository.create(
            blocker_id=self.user.user_id,
            blocked_id=self.blocked.user_id,
        )

        self.private = UserRepository.create(
            google_id=str(uuid.uuid4()),
            email="patrick@gmail.com",
            username="patrick",
        )
        updates = {"privacy": "private"}

        UserService.update_user_profile(self.private.user_id,**updates)

        self.admin = UserRepository.create(
            google_id=str(uuid.uuid4()),
            email="admin@gmail.com",
            username = "admin",
        )
        self.admin.is_admin = True
        self.admin.save()
        
        #self.domain = Domain.objects.create(domain_name='TestDomain', description='d')
        self.forum = Forum.objects.create(creator=self.user, forum_name='TestForum', description='d')
        # Create a valid subforum
        self.subforum = SubforumRepository.create(
            creator_id=self.user.user_id,
            subforum_name="General Discussion",
            description="Test subforum",

            parent_forum_id=self.forum.forum_id,
        )

        # Create posts inside that subforum
        self.post = PostRepository.create(
            user_id=self.user.user_id,
            subforum_id=self.subforum.subforum_id,
            title="Test Post",
            content="Hello world",

        )

        self.post_to_del = PostRepository.create(
            user_id=self.user.user_id,
            subforum_id=self.subforum.subforum_id,
            title="to del",
            content="to del",
        )
        self.post2 = PostRepository.create(
            user_id=self.viewer.user_id,
            subforum_id=self.subforum.subforum_id,
            title="Test Post",
            content="Hello world",

        )
        self.post_to_del2 = PostRepository.create(
            user_id=self.viewer.user_id,
            subforum_id=self.subforum.subforum_id,
            title="to del",
            content="to del",
        )

        self.privpost = PostRepository.create(
            user_id=self.private.user_id,
            subforum_id=self.subforum.subforum_id,
            title = "Happy anniversary NIcole",
            content= "Happy anniversary NIcole",
        )

        self.blockpost = PostRepository.create(
            user_id=self.blocked.user_id,
            subforum_id=self.subforum.subforum_id,
            title = "I hate Alice",
            content= "I HATE ALICE!!!!!!!!! >:("
        )

        self.follow= FollowRepository.create(follower_id=self.viewer.user_id, following_id=self.private.user_id)


        self.service = PostService()

        # ----------------------------------------------------------------------
        # TEST: get_post
        # ----------------------------------------------------------------------
    def test_get_post_as_owner(self):
        post = self.service.get_post_by_id(post_id=self.post.post_id)
        assert post.post_id == self.post.post_id

    def test_get_post_as_viewer(self):
            post = self.service.get_post_by_id(viewer_id=self.viewer.user_id, post_id=self.post.post_id)
            assert post.post_id == self.post.post_id

    def test_get_post_missing_raises_exception(self):
        with pytest.raises(NotFoundError):
            self.service.get_post_by_id(post_id=str(uuid.uuid4()))

    def test_get_post_as_blocked(self):
        with ((pytest.raises(PermissionDeniedError))):
            self.service.get_post_by_id(viewer_id=self.blocked.user_id,post_id=self.post.post_id)

    def test_get_post_as_blocker(self):
        with ((pytest.raises(PermissionDeniedError))):
            self.service.get_post_by_id(viewer_id=self.user.user_id,post_id=self.blockpost.post_id)

    def test_get_post_private_no_follow(self):
        with ((pytest.raises(PermissionDeniedError))):
            self.service.get_post_by_id(viewer_id=self.user.user_id,post_id=self.privpost.post_id)


    def test_get_post_private_with_follow(self):
        post = self.service.get_post_by_id(viewer_id=self.viewer.user_id,post_id=self.privpost.post_id)
        assert post.post_id == self.privpost.post_id
        assert post.user.user_id == self.private.user_id
    #def test_get_post_as_blocked(self):

        # ----------------------------------------------------------------------
        # TEST: delete_post
        # ----------------------------------------------------------------------
    def test_delete_post_by_owner(self):
        self.service.delete_post(user_id=self.user.user_id, post_id=self.post_to_del.post_id)
        assert not Post.objects.filter(post_id=self.post_to_del.post_id).exists()

    def test_delete_post_by_stranger_raises(self):
        with pytest.raises(PermissionDeniedError):
            self.service.delete_post(user_id=self.user.user_id, post_id=self.post_to_del2.post_id)


    def test_delete_as_admin(self):
        self.service.delete_post(user_id=self.admin.user_id, post_id=self.post_to_del2.post_id)
        assert not Post.objects.filter(post_id=self.post_to_del2.post_id).exists()
        # ----------------------------------------------------------------------
        # TEST: create_post
        # ----------------------------------------------------------------------
    def test_create_post(self):
        new_post = self.service.create_post(
            user_id=self.viewer.user_id,
            title="viewer's post",
            subforum_id=self.subforum.subforum_id,
            content="My first post!"
        )
        assert new_post.user == self.viewer
        assert new_post.content == "My first post!"
        assert new_post.subforum == self.subforum

    def test_create_post_invalid_subforum(self):
        with ((pytest.raises(NotFoundError))):
            self.service.create_post(
                user_id=self.viewer.user_id,subforum_id=str(uuid.uuid4()),title="whatever",content="Hi")

    def test_like_post(self):
        pre_like_count = self.post2.like_count+1
        like = self.service.like_post(post_id=self.post2.post_id, user_id=self.viewer.user_id)
        assert like.user.user_id == self.viewer.user_id
        assert like.post.post_id == self.post2.post_id
        assert pre_like_count == self.service.get_post_by_id(self.post2.post_id).like_count

    def test_like_post_has_blocked(self):
        with ((pytest.raises(PermissionDeniedError))):
            self.service.like_post(post_id=self.post.post_id, user_id=self.blocked.user_id)

    def test_like_post_has_blocker(self):
        with ((pytest.raises(PermissionDeniedError))):
            self.service.like_post(post_id=self.blockpost.post_id, user_id=self.user.user_id)

    def test_like_not_followed(self):
        with ((pytest.raises(PermissionDeniedError))):
            self.service.like_post(post_id=self.privpost.post_id, user_id=self.user.user_id)

    def test_like_follow_post(self):
        pre_like_count = self.service.get_post_by_id(self.privpost.post_id).like_count+1
        like = self.service.like_post(post_id=self.privpost.post_id, user_id=self.viewer.user_id)
        assert like.user.user_id == self.viewer.user_id
        assert like.post.post_id == self.privpost.post_id
        assert pre_like_count == self.service.get_post_by_id(self.privpost.post_id).like_count

    def test_unlike_post(self):
        self.service.like_post(post_id=self.post2.post_id, user_id=self.viewer.user_id)
        pre_like_count = self.service.get_post_by_id(self.post2.post_id).like_count-1
        self.service.unlike_post(post_id=self.post2.post_id, user_id=self.viewer.user_id)

        assert pre_like_count == self.service.get_post_by_id(self.post2.post_id).like_count

    def test_like_not_existing_post(self):
        with (pytest.raises(NotFoundError)):
            self.service.like_post(post_id=str(uuid.uuid4()), user_id=self.viewer.user_id)

    def test_like_twice(self):
        self.service.like_post(post_id=self.post2.post_id, user_id=self.viewer.user_id)
        with (pytest.raises(ConflictError)):
            self.service.like_post(post_id=self.post2.post_id, user_id=self.viewer.user_id)
    def test_unlike_no_liked_post(self):
        with(pytest.raises(NotFoundError)):
            self.service.unlike_post(post_id=self.post2.post_id, user_id=self.viewer.user_id)

    def test_get_no_likers(self):
        list_likes = self.service.get_post_likes(self.post2.post_id)
        assert len(list_likes) == 0

    def test_get_likers(self):
        like = self.service.like_post(post_id=self.post2.post_id, user_id=self.viewer.user_id)
        list_likes = self.service.get_post_likes(self.post2.post_id)
        assert list_likes[0].like_id == like.like_id
        assert list_likes[0].post.post_id == self.post2.post_id
        assert list_likes[0].user.user_id == self.viewer.user_id

    def test_get_like_from_no_post(self):
        with(pytest.raises(NotFoundError)):
            self.service.get_post_likes(str(uuid.uuid4()))

    def test_feed(self):
        feed = self.service.get_feed(self.viewer.user_id)
        assert len(feed) == 6

    def test_discover(self):
        self.service.like_post(post_id=self.post.post_id, user_id=self.viewer.user_id)
        self.service.like_post(post_id=self.post.post_id, user_id=self.private.user_id)
        self.service.like_post(post_id=self.post2.post_id, user_id=self.user.user_id)
        discover = self.service.get_discover()
        assert len(discover) == 6
        assert discover[0].post_id == self.post.post_id
        assert discover[1].post_id == self.post2.post_id


"""  @patch('db.repositories.post_repository.PostRepository')
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

        mock_validator.validate_post_title.assert_called_once_with("Test Title")
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
        mock_audit.create.assert_called_once()

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
    #Test successful post retrieval.
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
        #Test post retrieval fails when post doesn't exist.
        mock_post_repo.get_by_id.return_value = None

        with self.assertRaises(NotFoundError):
            PostService.get_post_by_id(self.post_id)

    @patch('db.repositories.post_repository.PostRepository')
    @patch('db.repositories.user_repository.BlockRepository')
    def test_get_post_by_id_blocked_user(self, mock_block_repo, mock_post_repo):
        #Test post retrieval fails when user is blocked
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
        #Test private post access denied when not following.
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
        #Test successful post deletion by owner.
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
        #Test post deletion fails when user is not authorized.
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
        #Test post deletion by admin.
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
        #Test successful post like.
        mock_post = Mock()
        mock_get_post.return_value = mock_post
        mock_like_repo.exists.return_value = False

        mock_like = Mock()
        mock_like_repo.create.return_value = mock_like

        result = PostService.like_post(self.post_id, self.user_id, self.ip_address)

        mock_like_repo.exists.assert_called_once_with(self.user_id, self.post_id)
        mock_like_repo.create.assert_called_once_with(self.user_id, self.post_id)
        mock_post_repo.increment_like_count.assert_called_once_with(self.post_id)
        mock_audit.create.assert_called_once()
        self.assertEqual(result, mock_like)

    @patch('services.apps_services.post_service.PostService.get_post_by_id')
    @patch('db.repositories.post_repository.LikeRepository')
    def test_like_post_already_liked(self, mock_like_repo, mock_get_post):
        #Test liking already liked post fails.
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
        #Test successful post unlike.
        mock_like_repo.exists.return_value = True

        PostService.unlike_post(self.post_id, self.user_id, self.ip_address)

        mock_like_repo.delete.assert_called_once_with(self.user_id, self.post_id)
        mock_post_repo.decrement_like_count.assert_called_once_with(self.post_id)
        mock_audit.create.assert_called_once()

    @patch('db.repositories.post_repository.LikeRepository')
    def test_unlike_post_not_liked(self, mock_like_repo):
        #Test unliking non-liked post fails.
        mock_like_repo.exists.return_value = False

        with self.assertRaises(NotFoundError):
            PostService.unlike_post(self.post_id, self.user_id)

    @patch('db.repositories.post_repository.PostRepository')
    @patch('db.repositories.post_repository.LikeRepository')
    def test_get_post_likes_success(self, mock_like_repo, mock_post_repo):
        #Test getting post likes.
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
        #Test getting likes for non-existent post fails.
        mock_post_repo.get_by_id.return_value = None

        with self.assertRaises(NotFoundError):
            PostService.get_post_likes(self.post_id)

    @patch('db.repositories.post_repository.PostRepository')
    def test_get_feed(self, mock_post_repo):
        #Test getting personalized feed.
        mock_posts = [Mock(), Mock(), Mock()]
        mock_post_repo.get_feed.return_value = mock_posts

        result = PostService.get_feed(self.user_id, page=1, page_size=20)

        #mock_post_repo.get_feed.assert_called_once_with(self.user_id, 1, 20)
        self.assertEqual(result, mock_posts)

    @patch('db.repositories.post_repository.PostRepository')
    def test_get_discover(self, mock_post_repo):
        #Test getting discover feed.
        mock_posts = [Mock(), Mock(), Mock()]
        mock_post_repo.get_discover.return_value = mock_posts

        result = PostService.get_discover(self.user_id, page=1, page_size=20)

        #mock_post_repo.get_discover.assert_called_once_with(self.user_id, 1, 20)
        self.assertEqual(result, mock_posts)

    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes_success(self, mock_get_likes):
        #Test successfully getting post likes.
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
        #Test getting likes for post with no likes.
        self.client.force_authenticate(user=self.user)
        mock_get_likes.return_value = []

        response = self.client.get(f'/api/likes/posts/{self.post_id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.data, [])


    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes_with_pagination(self, mock_get_likes):
        #Test getting post likes with custom pagination.
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
        #Test getting post likes from page 3.
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
        #Test getting post likes with invalid page parameter.
        self.client.force_authenticate(user=self.user)

    # This will raise ValueError when converting to int
        with self.assertRaises(ValueError):
            response = self.client.get(
                f'/api/likes/posts/{self.post_id}/',
                {'page': 'invalid'}
            )


    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes_service_error(self, mock_get_likes):
        #Test getting post likes when service raises error.
        self.client.force_authenticate(user=self.user)
        mock_get_likes.side_effect = NotFoundError("Post not found")

    # The view doesn't catch this exception, so it will propagate
        with self.assertRaises(NotFoundError):
            response = self.client.get(f'/api/likes/posts/{self.post_id}/')


    @patch('services.apps_services.post_service.PostService.get_post_likes')
    def test_get_post_likes_with_large_page_size(self, mock_get_likes):
        #Test getting post likes with large page size.
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
        #Test that default pagination values are used when not provided.
        self.client.force_authenticate(user=self.user)
        mock_get_likes.return_value = []

        response = self.client.get(f'/api/likes/posts/{self.post_id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should use default values: page=1, page_size=20
        #mock_get_likes.assert_called_once_with(self.post_id, 1, 20)


    @patch('services.apps_services.post_service.PostService.like_post')
    @patch('common.utils.get_client_ip')
    def test_like_post_ip_address_logged(self, mock_get_ip, mock_like_post):
        #Test that IP address is correctly passed to service.
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
         mock_like_post.assert_called_once_with(
            self.post_id,
            str(self.user_id),
            test_ip
        )


    @patch('services.apps_services.post_service.PostService.unlike_post')
    @patch('common.utils.get_client_ip')
    def test_unlike_post_ip_address_logged(self, mock_get_ip, mock_unlike_post):
        #Test that IP address is correctly passed to unlike service.
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
        )"""