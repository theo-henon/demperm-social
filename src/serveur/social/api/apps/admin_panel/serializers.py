"""
Serializers for admin panel.
"""
from rest_framework import serializers
from api.db.models import Report, User, Post, Comment


class AdminReportListSerializer(serializers.ModelSerializer):
    """Serializer for listing reports with target preview."""
    report_id = serializers.UUIDField(source='public_uuid', read_only=True)
    reporter = serializers.SerializerMethodField()
    target_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'report_id', 'reporter', 'target_type', 'target_id',
            'target_preview', 'reason', 'description', 'status', 'created_at'
        ]
    
    def get_reporter(self, obj):
        return {
            'user_id': str(obj.reporter.public_uuid),
            'username': obj.reporter.username
        }
    
    def get_target_preview(self, obj):
        """Get preview of reported content."""
        try:
            if obj.target_type == 'post':
                post = Post.objects.get(public_uuid=obj.target_id)
                return {
                    'title': post.title,
                    'content': post.content[:100] + '...' if len(post.content) > 100 else post.content
                }
            elif obj.target_type == 'comment':
                comment = Comment.objects.get(public_uuid=obj.target_id)
                return {
                    'content': comment.content[:100] + '...' if len(comment.content) > 100 else comment.content
                }
            elif obj.target_type == 'user':
                user = User.objects.get(public_uuid=obj.target_id)
                return {
                    'username': user.username,
                    'display_name': user.display_name or user.username
                }
        except (Post.DoesNotExist, Comment.DoesNotExist, User.DoesNotExist):
            return {'error': 'Target not found'}
        return None


class AdminReportResolveSerializer(serializers.Serializer):
    """Serializer for resolving a report."""
    action_taken = serializers.CharField(max_length=200)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)


class AdminUserBanSerializer(serializers.Serializer):
    """Serializer for banning a user."""
    reason = serializers.CharField(max_length=500)
    duration_days = serializers.IntegerField(required=False, allow_null=True, 
                                            help_text="Number of days for ban, null for permanent")


class AdminStatsUsersSerializer(serializers.Serializer):
    """Serializer for user statistics."""
    total_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    new_users_this_week = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    banned_users = serializers.IntegerField()


class AdminStatsPostsSerializer(serializers.Serializer):
    """Serializer for post statistics."""
    total_posts = serializers.IntegerField()
    posts_today = serializers.IntegerField()
    posts_this_week = serializers.IntegerField()
    deleted_posts = serializers.IntegerField()


class AdminStatsActivitySerializer(serializers.Serializer):
    """Serializer for activity statistics."""
    total_comments = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    total_reports = serializers.IntegerField()
    pending_reports = serializers.IntegerField()
    active_conversations = serializers.IntegerField()
