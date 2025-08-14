from rest_framework import serializers
from django.contrib.auth import get_user_model
from .mixins import BaseModel

User = get_user_model()


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
