import time
import uuid
from multiprocessing.connection import wait

import pytest
import unittest
from unittest import mock
from rest_framework import status
from datetime import datetime

from rest_framework.exceptions import NotFound

from services.apps_services.post_service import PostService
from services.apps_services.comment_service import CommentService
from services.apps_services.user_service import UserService
from common.exceptions import NotFoundError, ValidationError, PermissionDeniedError
from db.entities.post_entity import Comment
from rest_framework import status
from db.repositories.user_repository import UserRepository, BlockRepository, FollowRepository
from db.repositories.post_repository import PostRepository, CommentRepository
from db.repositories.domain_repository import SubforumRepository
from db.entities.domain_entity import Forum, Subforum


"""def create_mock_comment(comment_id, post_id, user_id, content, parent_comment_id=None):
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
@mock.patch('common.validators.Validator')"""

class CommentServiceTests(unittest.TestCase):

    def setUp(self):
        # Define common IDs for testing
        self.user = UserRepository.create(
            google_id=str(uuid.uuid4()),
            email="user@gmail.com",
            username="alice",

        )

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
        # self.domain = Domain.objects.create(domain_name='TestDomain', description='d')
        self.forum = Forum.objects.create(creator=self.user, forum_name='TestForum', description='d')
        # Create a valid subforum
        self.subforum = SubforumRepository.create(
            creator_id=self.user.user_id,
            subforum_name="General Discussion",
            description="Test subforum",

            parent_forum_id=self.forum.forum_id,
        )

        # Create a post inside that subforum
        self.post = PostRepository.create(
            user_id=self.user.user_id,
            subforum_id=self.subforum.subforum_id,
            title="Test Post",
            content="Hello world",

        )
        self.post2 = PostRepository.create(
            user_id=self.viewer.user_id,
            subforum_id=self.subforum.subforum_id,
            title="Test Post",
            content="Hello world",

        )
        self.private = UserRepository.create(
            google_id=str(uuid.uuid4()),
            email="patrick@gmail.com",
            username="patrick",
        )
        updates = {"privacy": "private"}

        UserService.update_user_profile(self.private.user_id, **updates)

        self.privpost = PostRepository.create(
            user_id=self.private.user_id,
            subforum_id=self.subforum.subforum_id,
            title="Happy anniversary NIcole",
            content="Happy anniversary NIcole",
        )

        self.follow= FollowRepository.create(follower_id=self.viewer.user_id, following_id=self.private.user_id)


        self.comment = CommentRepository.create(self.user.user_id, self.post.post_id,"Nice",None)

        self.service = CommentService()

    def test_get_comment_by_id(self):
        one_comment = self.service.get_comment_by_id(self.comment.comment_id)
        assert one_comment.comment_id == self.comment.comment_id
        assert one_comment.user.user_id == self.user.user_id
        assert one_comment.post.post_id == self.post.post_id

    def test_get_comment_by_non_id(self):
        with pytest.raises(NotFoundError):
            self.service.get_comment_by_id(str(uuid.uuid4()))


    def test_create_comment(self):

        precount = PostService.get_post_by_id(self.post.post_id).comment_count+1
        new_comment = self.service.create_comment(self.viewer.user_id,self.post.post_id,"Meh",None)
        assert new_comment.user.user_id == self.viewer.user_id
        assert new_comment.post.post_id == self.post.post_id
        assert new_comment.content == "Meh"
        assert PostService.get_post_by_id(self.post.post_id).comment_count ==  precount



    def test_create_comment_non_post(self):
        with (pytest.raises(NotFoundError)):
            self.service.create_comment(self.viewer.user_id,str(uuid.uuid4()),"Nice",None)

    def test_comment_as_blocked(self):
        with(pytest.raises(PermissionDeniedError)):
            self.service.create_comment(self.blocked.user_id,self.post.post_id,"I hate you ALice",None)

    def test_comment_private_no_follow(self):
        with(pytest.raises(PermissionDeniedError)):
            self.service.create_comment(self.user.user_id,self.privpost.post_id,"Meh",None)

    def test_comment_private_follow(self):
        commentcount = PostService.get_post_by_id(self.privpost.post_id).comment_count+1
        new_comment = self.service.create_comment(self.viewer.user_id, self.privpost.post_id, "Meh", None)
        assert new_comment.user.user_id == self.viewer.user_id
        assert new_comment.post.post_id == self.privpost.post_id
        assert new_comment.content == "Meh"
        assert PostService.get_post_by_id(self.privpost.post_id).comment_count == commentcount

    def test_get_one_from_post(self):
        single = self.service.get_post_comments(self.post.post_id)
        assert len(single) == 1
        assert single[0].comment_id == self.comment.comment_id
        assert single[0].post.post_id == self.post.post_id

    def test_get_no_comment_from_post(self):
        zero = self.service.get_post_comments(self.post2.post_id)
        assert len(zero) == 0

    def test_get_comment_from_no_post(self):
        with pytest.raises(NotFoundError):
            self.service.get_post_comments(str(uuid.uuid4()))

    def test_get_multiple_comments(self):
        second = self.service.create_comment(self.viewer.user_id,self.post.post_id,"Meh",None)
        time.sleep(4)
        third = self.service.create_comment(self.private.user_id,self.post.post_id,"cool",None)
        three = self.service.get_post_comments(self.post.post_id)
        assert len(three) == 3
        assert three[2].comment_id == self.comment.comment_id
        assert three[2].post.post_id == self.post.post_id
        assert three[2].user.user_id == self.user.user_id
        assert three[1].comment_id == second.comment_id
        assert three[1].post.post_id == self.post.post_id
        assert three[1].user.user_id == self.viewer.user_id
        assert three[0].comment_id == third.comment_id
        assert three[0].post.post_id == self.post.post_id
        assert three[0].user.user_id == self.private.user_id

    def test_make_reply(self):

        nb_comment = PostService.get_post_by_id(self.post.post_id).comment_count+1
        reply = self.service.create_comment(self.viewer.user_id,self.post.post_id,"Noice",self.comment.comment_id)
        assert reply.user.user_id == self.viewer.user_id
        assert reply.post.post_id == self.post.post_id
        assert reply.content == "Noice"
        assert reply.parent_comment.comment_id == self.comment.comment_id
        assert nb_comment == PostService.get_post_by_id(self.post.post_id).comment_count

    def test_make_reply_to_no_post(self):
        with pytest.raises(NotFoundError):
            self.service.create_comment(self.viewer.user_id,str(uuid.uuid4()),"Meh",self.comment.comment_id)

    def test_make_reply_to_non_comment(self):
        with pytest.raises(NotFoundError):
            self.service.create_comment(self.viewer.user_id,self.post.post_id,"Meh",str(uuid.uuid4()))

    def test_make_reply_to_comment_from_wrong_post(self):
        with pytest.raises(ValidationError):
            self.service.create_comment(self.viewer.user_id,self.post2.post_id,"Meh",self.comment.comment_id)


    def test_reply_while_blocked(self):
        with pytest.raises(PermissionDeniedError):
            self.service.create_comment(self.blocked.user_id,self.post.post_id,"Meh",self.comment.comment_id)

        comment2=self.service.create_comment(self.user.user_id,self.post2.post_id,"Meh",None)
        with pytest.raises(PermissionDeniedError):
            self.service.create_comment(self.blocked.user_id,self.post2.post_id,"Meh",comment2.comment_id)


    def test_reply_private_follow(self):
        new_comment = self.service.create_comment(self.viewer.user_id, self.privpost.post_id, "Meh", None)
        nb_comment = PostService.get_post_by_id(self.privpost.post_id).comment_count+1

        new_reply = self.service.create_comment(self.viewer.user_id, self.privpost.post_id, "Meh", new_comment.comment_id)
        assert new_reply.user.user_id == self.viewer.user_id
        assert new_reply.post.post_id == self.privpost.post_id
        assert new_reply.parent_comment.comment_id == new_comment.comment_id
        assert nb_comment == PostService.get_post_by_id(self.privpost.post_id).comment_count



    def test_reply_private_no_follow(self):
        private_reply = self.service.create_comment(self.viewer.user_id, self.privpost.post_id, "Meh", None)
        with (pytest.raises(PermissionDeniedError)):
            self.service.create_comment(self.user.user_id,self.privpost.post_id,"Meh",private_reply.comment_id)

    def test_delete_comment(self):
        nb_comment = PostService.get_post_by_id(self.post.post_id).comment_count
        todel = self.service.create_comment(self.user.user_id,self.post.post_id,"Meh",None)
        self.service.delete_comment(todel.comment_id,self.user.user_id)
        assert nb_comment == PostService.get_post_by_id(self.post.post_id).comment_count
        with (pytest.raises(NotFoundError)):
            self.service.get_comment_by_id(todel.comment_id)

    def test_delete_no_post(self):
        with pytest.raises(NotFoundError):
            self.service.delete_comment(str(uuid.uuid4()),self.user.user_id)

    def test_delete_wrong_user(self):
        with pytest.raises(NotFoundError):
            self.service.delete_comment(self.comment.comment_id,str(uuid.uuid4()))

    def test_delete_replies(self):
        nbcomment = PostService.get_post_by_id(self.post.post_id).comment_count
        reply = self.service.create_comment(self.user.user_id,self.post.post_id,"Meh",self.comment.comment_id)
        self.service.delete_comment(reply.comment_id,self.user.user_id)
        assert nbcomment == PostService.get_post_by_id(self.post.post_id).comment_count
        with (pytest.raises(NotFoundError)):
            self.service.get_comment_by_id(reply.comment_id)

    def test_delete_cascade(self):
        nb_comment = PostService.get_post_by_id(self.post.post_id).comment_count
        todel = self.service.create_comment(self.user.user_id,self.post.post_id,"Meh",None)
        tocascade = self.service.create_comment(self.user.user_id,self.post.post_id,"Meh",todel.comment_id)

        self.service.delete_comment(todel.comment_id,self.user.user_id)
        assert nb_comment == PostService.get_post_by_id(self.post.post_id).comment_count
        with (pytest.raises(NotFoundError)):
            self.service.get_comment_by_id(todel.comment_id)
        with (pytest.raises(NotFoundError)):
            self.service.get_comment_by_id(tocascade.comment_id)


    



        """
    def test_create_comment_success(self, MockValidator, MockCommentRepository, MockPostRepository,
                                    MockAuditLogRepository):
        #Test successful creation of a top-level comment.
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
        #Test error when post does not exist.
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
        #Test error when parent comment does not exist for a reply.
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
        #Test error when parent comment belongs to a different post.
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
        #Test successful retrieval of a comment.
        mock_comment = create_mock_comment(self.comment_id, self.post_id, self.user_id, self.content)
        MockCommentRepository.get_by_id.return_value = mock_comment

        comment = CommentService.get_comment_by_id(self.comment_id)

        self.assertEqual(comment.comment_id, self.comment_id)
        #MockCommentRepository.get_by_id.assert_called_once_with(self.comment_id)

    def test_get_comment_by_id_not_found(self, MockCommentRepository):
        #Test error when comment is not found.
        MockCommentRepository.get_by_id.return_value = None

        with self.assertRaisesRegex(NotFoundError, f"Comment {self.comment_id} not found"):
            CommentService.get_comment_by_id(self.comment_id)

    def test_delete_comment_owner_success(self, MockUserRepository, MockCommentRepository, MockPostRepository,
                                          MockAuditLogRepository):
        #Test successful deletion by the comment owner.
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
        #Test successful deletion by an admin user.
        comment_owner_id = 'user-owner'
        admin_user_id = 'user-admin'
        comment_to_delete = create_mock_comment(self.comment_id, self.post_id, comment_owner_id, self.content)

        with mock.patch.object(CommentService, 'get_comment_by_id', return_value=comment_to_delete):
            MockUserRepository.get_by_id.return_value = create_mock_user(admin_user_id, is_admin=True)

            CommentService.delete_comment(self.comment_id, admin_user_id, self.ip_address)

            MockCommentRepository.delete.assert_called_once()
            MockPostRepository.decrement_comment_count.assert_called_once()

    def test_delete_comment_permission_denied(self, MockUserRepository, MockCommentRepository, MockPostRepository):
        #Test error when a non-owner/non-admin tries to delete.
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
        #Test error when getting comments for a non-existent post.
        MockPostRepository.get_by_id.return_value = None

        with self.assertRaisesRegex(NotFoundError, f"Post {self.post_id} not found"):
            CommentService.get_post_comments(self.post_id)

        #MockCommentRepository.get_by_post.assert_not_called()

    def test_get_post_comments_success(self, MockCommentRepository, MockPostRepository):
        #Test successful retrieval of post comments.
        MockPostRepository.get_by_id.return_value = mock.Mock()
        mock_comments = [create_mock_comment(f'c-{i}', self.post_id, self.user_id, 'content') for i in range(2)]
        MockCommentRepository.get_by_post.return_value = mock_comments

        comments = CommentService.get_post_comments(self.post_id, page=2, page_size=10, sort_by='like_count')

        self.assertEqual(len(comments), 2)
        #MockCommentRepository.get_by_post.assert_called_once_with(self.post_id, 2, 10, 'like_count')

    def test_get_comment_replies_success(self, MockCommentRepository):
        #Test successful retrieval of replies to a comment.
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
        #Test error when retrieving replies for a non-existent comment.
        # Mocking the internal call to get_comment_by_id
        with mock.patch.object(CommentService, 'get_comment_by_id', side_effect=NotFoundError("Comment not found")):
            with self.assertRaises(NotFoundError):
                CommentService.get_comment_replies(self.comment_id)

       # MockCommentRepository.get_replies.assert_not_called()"""