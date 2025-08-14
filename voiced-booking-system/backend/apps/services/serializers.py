from rest_framework import serializers
from apps.core.serializers import TenantFilteredSerializer, CountSerializerMixin, TimeFieldsMixin
from .models import Service, ServiceCategory, ServiceProvider


class ServiceCategorySerializer(TenantFilteredSerializer, CountSerializerMixin):
    services_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceCategory
        fields = '__all__'
    
    def get_services_count(self, obj):
        return self.get_active_count(obj, 'services')


class ServiceProviderSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = ServiceProvider
        fields = ['id', 'user', 'user_name', 'user_email', 'is_primary', 'is_active']


class ServiceSerializer(TenantFilteredSerializer, TimeFieldsMixin, CountSerializerMixin):
    category_name = serializers.CharField(source='category.name', read_only=True)
    providers = ServiceProviderSerializer(many=True, read_only=True)
    providers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = '__all__'
    
    def get_providers_count(self, obj):
        return self.get_active_count(obj, 'providers')


class ServiceCreateSerializer(TenantFilteredSerializer):
    provider_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Service
        fields = '__all__'
        extra_kwargs = {
            'provider_ids': {'write_only': True}
        }
    
    def create(self, validated_data):
        provider_ids = validated_data.pop('provider_ids', [])
        service = super().create(validated_data)
        
        if provider_ids:
            from apps.users.models import User
            for i, provider_id in enumerate(provider_ids):
                try:
                    user = User.objects.get(id=provider_id)
                    ServiceProvider.objects.create(
                        service=service,
                        user=user,
                        is_primary=(i == 0)
                    )
                except User.DoesNotExist:
                    pass
        
        return service


class ServiceUpdateSerializer(TenantFilteredSerializer):
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['business']


class ServiceListSerializer(serializers.ModelSerializer, CountSerializerMixin):
    category_name = serializers.CharField(source='category.name', read_only=True)
    duration_display = serializers.ReadOnlyField()
    providers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'category_name', 'duration', 'duration_display', 
                 'price', 'is_active', 'online_booking_enabled', 'voice_booking_enabled',
                 'providers_count']
    
    def get_providers_count(self, obj):
        return self.get_active_count(obj, 'providers')
