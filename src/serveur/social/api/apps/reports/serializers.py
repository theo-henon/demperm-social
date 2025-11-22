"""
Serializers for reports.
"""
from rest_framework import serializers
from api.db.models import Report


class ReportCreateSerializer(serializers.Serializer):
    """Serializer for creating a report."""
    target_type = serializers.ChoiceField(choices=['post', 'comment', 'user'])
    target_id = serializers.UUIDField()
    reason = serializers.ChoiceField(choices=['spam', 'harassment', 'inappropriate', 'misinformation', 'other'])
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_description(self, value):
        """Sanitize description."""
        if value:
            return value.strip()
        return value


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for report response."""
    report_id = serializers.UUIDField(source='public_uuid', read_only=True)
    
    class Meta:
        model = Report
        fields = ['report_id', 'status', 'created_at']
