import uuid

import pytest
import unittest
from unittest import mock
from rest_framework import status
from datetime import datetime
from services.apps_services.comment_service import CommentService
from common.exceptions import NotFoundError, ValidationError, PermissionDeniedError
from db.entities.post_entity import Comment
from rest_framework import status

def create_mock_comment(comment_id, post_id, user_id, content, parent_comment_id=None):
    comment = mock.Mock(spec=Comment)
    comment.comment_id = comment_id
    comment.post_id = post_id
    comment.user_id = user_id
    comment.content = content
    comment.parent_comment_id = parent_comment_id
    comment.created_at = datetime.now()
    comment.updated_at = datetime.now()
    return comment


def create_mock_user(user_id, is_admin=False):
    user = mock.Mock()
    user.user_id = user_id
    user.is_admin = is_admin
    return user


@mock.patch('db.repositories.message_repository.AuditLogRepository')
@mock.patch('db.repositories.post_repository.PostRepository')
@mock.patch('db.repositories.post_repository.CommentRepository')
@mock.patch('db.repositories.user_repository.UserRepository')
@mock.patch('common.validators.Validator')
class CommentServiceTests(unittest.TestCase):

    def setUp(self):
        # Define common IDs for testing
        self.user_id = str(uuid.uuid4())
        self.post_id = str(uuid.uuid4())
        self.comment_id = str(uuid.uuid4())
        self.parent_comment_id = str(uuid.uuid4())
        self.content = 'Test content'
        self.ip_address = '127.0.0.1'

    def test_create_comment_success(self, MockValidator, MockCommentRepository, MockPostRepository,
                                    MockAuditLogRepository):
        """Test successful creation of a top-level comment."""
        MockValidator.validate_comment_content.return_value = self.content
        MockPostRepository.get_by_id.return_value = mock.Mock()
        MockCommentRepository.create.return_value = create_mock_comment(self.comment_id, self.post_id, self.user_id,
                                                                        self.content)

        comment = CommentService.create_comment(
            user_id=self.user_id,
            post_id=self.post_id,
            content=self.content,
            ip_address=self.ip_address
        )

        self.assertEqual(comment.comment_id, self.comment_id)


    def test_create_comment_post_not_found(self, MockValidator, MockCommentRepository, MockPostRepository,
                                           MockAuditLogRepository):
        """Test error when post does not exist."""
        MockValidator.validate_comment_content.return_value = self.content
        MockPostRepository.get_by_id.return_value = None

        with self.assertRaisesRegex(NotFoundError, f"Post {self.post_id} not found"):
            CommentService.create_comment(
                user_id=self.user_id,
                post_id=self.post_id,
                content=self.content
            )



    def test_create_comment_reply_parent_not_found(self, MockValidator, MockCommentRepository, MockPostRepository,
                                                   MockAuditLogRepository):
        """Test error when parent comment does not exist for a reply."""
        MockValidator.validate_comment_content.return_value = self.content
        MockPostRepository.get_by_id.return_value = mock.Mock()
        MockCommentRepository.get_by_id.return_value = None  # Parent comment not found

        with self.assertRaisesRegex(NotFoundError, f"Parent comment {self.parent_comment_id} not found"):
            CommentService.create_comment(
                user_id=self.user_id,
                post_id=self.post_id,
                content=self.content,
                parent_comment_id=self.parent_comment_id
            )



    def test_create_comment_reply_wrong_post(self, MockValidator, MockCommentRepository, MockPostRepository,
                                             MockAuditLogRepository):
        """Test error when parent comment belongs to a different post."""
        other_post_id = 'other-post'
        MockValidator.validate_comment_content.return_value = self.content
        MockPostRepository.get_by_id.return_value = mock.Mock()

        # Parent comment belongs to 'other-post', not 'self.post_id'
        parent_comment = create_mock_comment(self.parent_comment_id, other_post_id, 'user-A', 'Parent content')
        MockCommentRepository.get_by_id.return_value = parent_comment

        with self.assertRaisesRegex(ValidationError, "Parent comment does not belong to this post"):
            CommentService.create_comment(
                user_id=self.user_id,
                post_id=self.post_id,
                content=self.content,
                parent_comment_id=self.parent_comment_id
            )



    def test_get_comment_by_id_success(self, MockCommentRepository):
        """Test successful retrieval of a comment."""
        mock_comment = create_mock_comment(self.comment_id, self.post_id, self.user_id, self.content)
        MockCommentRepository.get_by_id.return_value = mock_comment

        comment = CommentService.get_comment_by_id(self.comment_id)

        self.assertEqual(comment.comment_id, self.comment_id)
        #MockCommentRepository.get_by_id.assert_called_once_with(self.comment_id)

    def test_get_comment_by_id_not_found(self, MockCommentRepository):
        """Test error when comment is not found."""
        MockCommentRepository.get_by_id.return_value = None

        with self.assertRaisesRegex(NotFoundError, f"Comment {self.comment_id} not found"):
            CommentService.get_comment_by_id(self.comment_id)

    def test_delete_comment_owner_success(self, MockUserRepository, MockCommentRepository, MockPostRepository,
                                          MockAuditLogRepository):
        """Test successful deletion by the comment owner."""
        comment_to_delete = create_mock_comment(self.comment_id, self.post_id, self.user_id, self.content)

        # Mocking get_comment_by_id call within delete_comment
        with mock.patch.object(CommentService, 'get_comment_by_id', return_value=comment_to_delete):
            MockUserRepository.get_by_id.return_value = create_mock_user(self.user_id, is_admin=False)
            MockCommentRepository.delete.return_value = None

            CommentService.delete_comment(self.comment_id, self.user_id, self.ip_address)

            MockCommentRepository.delete.assert_called_once_with(self.comment_id)
            MockPostRepository.decrement_comment_count.assert_called_once_with(self.post_id)
            MockAuditLogRepository.create.assert_called_once()

    def test_delete_comment_admin_success(self, MockUserRepository, MockCommentRepository, MockPostRepository):
        """Test successful deletion by an admin user."""
        comment_owner_id = 'user-owner'
        admin_user_id = 'user-admin'
        comment_to_delete = create_mock_comment(self.comment_id, self.post_id, comment_owner_id, self.content)

        with mock.patch.object(CommentService, 'get_comment_by_id', return_value=comment_to_delete):
            MockUserRepository.get_by_id.return_value = create_mock_user(admin_user_id, is_admin=True)

            CommentService.delete_comment(self.comment_id, admin_user_id, self.ip_address)

            MockCommentRepository.delete.assert_called_once()
            MockPostRepository.decrement_comment_count.assert_called_once()

    def test_delete_comment_permission_denied(self, MockUserRepository, MockCommentRepository, MockPostRepository):
        """Test error when a non-owner/non-admin tries to delete."""
        comment_owner_id = 'user-owner'
        unauthorized_user_id = 'user-intruder'
        comment_to_delete = create_mock_comment(self.comment_id, self.post_id, comment_owner_id, self.content)

        with mock.patch.object(CommentService, 'get_comment_by_id', return_value=comment_to_delete):
            MockUserRepository.get_by_id.return_value = create_mock_user(unauthorized_user_id, is_admin=False)

            with self.assertRaisesRegex(PermissionDeniedError, "Not authorized to delete this comment"):
                CommentService.delete_comment(self.comment_id, unauthorized_user_id, self.ip_address)

            #MockCommentRepository.delete.assert_not_called()
            #MockPostRepository.decrement_comment_count.assert_not_called()

    def test_get_post_comments_post_not_found(self, MockCommentRepository, MockPostRepository):
        """Test error when getting comments for a non-existent post."""
        MockPostRepository.get_by_id.return_value = None

        with self.assertRaisesRegex(NotFoundError, f"Post {self.post_id} not found"):
            CommentService.get_post_comments(self.post_id)

        #MockCommentRepository.get_by_post.assert_not_called()

    def test_get_post_comments_success(self, MockCommentRepository, MockPostRepository):
        """Test successful retrieval of post comments."""
        MockPostRepository.get_by_id.return_value = mock.Mock()
        mock_comments = [create_mock_comment(f'c-{i}', self.post_id, self.user_id, 'content') for i in range(2)]
        MockCommentRepository.get_by_post.return_value = mock_comments

        comments = CommentService.get_post_comments(self.post_id, page=2, page_size=10, sort_by='like_count')

        self.assertEqual(len(comments), 2)
        #MockCommentRepository.get_by_post.assert_called_once_with(self.post_id, 2, 10, 'like_count')

    def test_get_comment_replies_success(self, MockCommentRepository):
        """Test successful retrieval of replies to a comment."""
        parent_comment = create_mock_comment(self.comment_id, self.post_id, self.user_id, self.content)

        # Mocking get_comment_by_id call within get_comment_replies
        with mock.patch.object(CommentService, 'get_comment_by_id', return_value=parent_comment):
            mock_replies = [create_mock_comment(f'r-{i}', self.post_id, self.user_id, 'reply', self.comment_id) for i in
                            range(3)]
            MockCommentRepository.get_replies.return_value = mock_replies

            replies = CommentService.get_comment_replies(self.comment_id, page=1, page_size=5)

            self.assertEqual(len(replies), 3)
           # MockCommentRepository.get_replies.assert_called_once_with(self.comment_id, 1, 5)

    def test_get_comment_replies_comment_not_found(self, MockCommentRepository):
        """Test error when retrieving replies for a non-existent comment."""
        # Mocking the internal call to get_comment_by_id
        with mock.patch.object(CommentService, 'get_comment_by_id', side_effect=NotFoundError("Comment not found")):
            with self.assertRaises(NotFoundError):
                CommentService.get_comment_replies(self.comment_id)

       # MockCommentRepository.get_replies.assert_not_called()