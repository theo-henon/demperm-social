"""
Serializers pour l'app subscriptions
"""
from rest_framework import serializers
from core.models import ForumSubscription


class ForumSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer pour un abonnement à un forum"""
    forum_uuid = serializers.UUIDField(source='forum.public_uuid', read_only=True)
    forum_name = serializers.CharField(source='forum.name', read_only=True)
    
    class Meta:
        model = ForumSubscription
        fields = ['forum_uuid', 'forum_name', 'created_at']
        read_only_fields = ['created_at']
