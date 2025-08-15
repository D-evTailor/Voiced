from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseSerializerMixin:
    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)
    business = serializers.StringRelatedField(read_only=True)
    
    @property
    def read_only_fields(self):
        return ('id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'business', 'deleted_at', 'deleted_by')


class DisplayFieldsMixin:
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    end_time = serializers.ReadOnlyField()
    duration_display = serializers.ReadOnlyField()
    
    def get_active_count(self, obj, relation_name):
        return getattr(obj, relation_name).filter(is_active=True).count()


class BaseSerializer(serializers.ModelSerializer, BaseSerializerMixin):
    class Meta:
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.Meta, 'read_only_fields'):
            self.Meta.read_only_fields = tuple(set(list(self.Meta.read_only_fields) + list(self.read_only_fields)))
        else:
            self.Meta.read_only_fields = self.read_only_fields


class TenantFilteredSerializer(BaseSerializer):
    def create(self, validated_data):
        request = self.context['request']
        validated_data.update({
            'created_by': request.user,
            'business': request.business
        })
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)
