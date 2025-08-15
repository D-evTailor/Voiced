from rest_framework import serializers
from apps.businesses.models import Business
from .multi_tenant_services import TenantRegistrationService
from .tasks import register_tenant_async


class TenantRegistrationSerializer(serializers.Serializer):
    business_name = serializers.CharField(max_length=200)
    business_slug = serializers.SlugField(max_length=50)
    business_email = serializers.EmailField()
    business_phone = serializers.CharField(max_length=17)
    business_address = serializers.CharField()
    business_city = serializers.CharField(max_length=100)
    business_type = serializers.CharField(max_length=50)
    area_code = serializers.CharField(max_length=10, required=False)
    async_processing = serializers.BooleanField(default=True)
    
    def validate_business_slug(self, value):
        if Business.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Business slug already exists")
        return value
    
    def create(self, validated_data):
        async_processing = validated_data.pop('async_processing', True)
        area_code = validated_data.pop('area_code', None)
        
        business = Business.objects.create(
            name=validated_data['business_name'],
            slug=validated_data['business_slug'],
            email=validated_data['business_email'],
            phone=validated_data['business_phone'],
            address=validated_data['business_address'],
            city=validated_data['business_city'],
            business_type=validated_data['business_type'],
            owner=self.context['request'].user
        )
        
        if async_processing:
            register_tenant_async.delay(business.id, area_code)
            return {
                'business': business,
                'vapi_setup': 'processing_async',
                'message': 'Business created, VAPI setup in progress'
            }
        else:
            service = TenantRegistrationService()
            result = service.register_tenant(business, area_code)
            return {
                'business': business,
                'vapi_setup': result,
                'message': 'Business created and VAPI configured'
            }
