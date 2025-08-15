from rest_framework import serializers
from apps.core.serializers import TenantFilteredSerializer, DisplayFieldsMixin
from .models import Business, BusinessHours, BusinessMember


class BusinessListSerializer(serializers.ModelSerializer):
    member_role = serializers.SerializerMethodField()
    is_primary = serializers.SerializerMethodField()
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'slug', 'business_type', 'logo', 'member_role', 'is_primary']
    
    def get_member_role(self, obj):
        user = self.context['request'].user
        member = obj.members.filter(user=user).first()
        return member.role if member else None
    
    def get_is_primary(self, obj):
        user = self.context['request'].user
        member = obj.members.filter(user=user).first()
        return member.is_primary if member else False


class AdditionalBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['name', 'business_type', 'email', 'phone', 'address', 'city', 'state', 'postal_code', 'country']
    
    def create(self, validated_data):
        from .services import BusinessRegistrationService
        user = self.context['request'].user
        service = BusinessRegistrationService()
        return service.create_additional_business(user, validated_data)


class BusinessHoursSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = BusinessHours
        fields = ['id', 'day_of_week', 'day_name', 'open_time', 'close_time', 'is_closed', 'is_open']


class BusinessMemberSerializer(serializers.ModelSerializer, DisplayFieldsMixin):
    
    class Meta:
        model = BusinessMember
        fields = ['id', 'user', 'user_email', 'user_name', 'role', 'role_display', 
                 'permissions', 'is_primary', 'is_active', 'joined_at']
        read_only_fields = ['joined_at']


class BusinessSerializer(serializers.ModelSerializer, DisplayFieldsMixin):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    full_address = serializers.CharField(read_only=True)
    business_hours = BusinessHoursSerializer(many=True, read_only=True)
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Business
        fields = '__all__'
        read_only_fields = ['owner', 'subscription_status', 'trial_ends_at']
    
    def get_members_count(self, obj):
        return self.get_active_count(obj, 'members')


class BusinessCreateSerializer(serializers.ModelSerializer):
    business_hours = BusinessHoursSerializer(many=True, required=False)
    
    class Meta:
        model = Business
        fields = ['name', 'slug', 'description', 'email', 'phone', 'website', 'address', 
                 'city', 'state', 'postal_code', 'country', 'locale', 'timezone', 'currency',
                 'allow_online_booking', 'allow_voice_booking', 'require_approval', 
                 'logo', 'primary_color', 'business_hours']
    
    def create(self, validated_data):
        from apps.core.factories import BusinessHoursFactory, BusinessMemberFactory
        
        business_hours_data = validated_data.pop('business_hours', [])
        business = super().create(validated_data)
        
        BusinessHoursFactory.create_business_hours(business, business_hours_data)
        BusinessMemberFactory.create_owner_membership(business)
        
        return business


class BusinessUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['name', 'description', 'email', 'phone', 'website', 'address',
                 'city', 'state', 'postal_code', 'country', 'timezone', 'currency',
                 'allow_online_booking', 'allow_voice_booking', 'require_approval',
                 'logo', 'primary_color']
