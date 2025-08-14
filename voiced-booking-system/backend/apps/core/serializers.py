from rest_framework import serializers
from django.contrib.auth import get_user_model
from .mixins import BaseModel

User = get_user_model()


class CountSerializerMixin:
    def get_active_count(self, obj, relation_name):
        return getattr(obj, relation_name).filter(is_active=True).count()


class UserFieldsMixin:
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)


class DisplayFieldsMixin:
    @property
    def display_fields(self):
        return {
            'status_display': serializers.CharField(source='get_status_display', read_only=True),
            'type_display': serializers.CharField(source='get_type_display', read_only=True),
            'role_display': serializers.CharField(source='get_role_display', read_only=True),
        }


class TimeFieldsMixin:
    end_time = serializers.ReadOnlyField()
    duration_display = serializers.ReadOnlyField()
    total_time_required = serializers.ReadOnlyField()


class BaseSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)
    business = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'business', 'deleted_at', 'deleted_by')


class TenantFilteredSerializer(BaseSerializer):
    def create(self, validated_data):
        user = self.context['request'].user
        business = self.context['request'].business
        validated_data['created_by'] = user
        validated_data['business'] = business
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        validated_data['updated_by'] = user
        return super().update(instance, validated_data)


class AuditSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    user_email = serializers.EmailField(read_only=True)
    
    class Meta:
        fields = '__all__'
        read_only_fields = '__all__'


class MetricsSerializer(serializers.ModelSerializer):
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    
    class Meta:
        fields = '__all__'
        read_only_fields = '__all__'
