from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.serializers import BaseSerializer, BaseBusinessFieldsMixin
from .models import UserProfile

User = get_user_model()


class UserBusinessRegistrationSerializer(BaseBusinessFieldsMixin, serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    locale = serializers.CharField(max_length=10, default='es')
    timezone = serializers.CharField(max_length=50, default='Europe/Madrid')
    
    def validate(self, attrs):
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'User with this email already exists'})
        return attrs
    
    def create(self, validated_data):
        from apps.businesses.services import BusinessRegistrationService
        
        user_data = {
            'email': validated_data['email'],
            'password': validated_data['password'],
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'locale': validated_data['locale'],
            'timezone': validated_data['timezone'],
        }
        
        business_data = {
            'name': validated_data['name'],
            'business_type': validated_data['business_type'],
            'email': validated_data['email'],
            'phone': validated_data['phone'],
            'address': validated_data.get('address', ''),
            'city': validated_data.get('city', ''),
            'state': validated_data.get('state', ''),
            'postal_code': validated_data.get('postal_code', ''),
            'country': validated_data.get('country', ''),
        }
        
        service = BusinessRegistrationService()
        user, business = service.create_business(user_data=user_data, business_data=business_data)
        
        return {'user': user, 'business': business}


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'avatar', 'email_notifications', 'sms_notifications', 'marketing_emails']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    display_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'display_name', 
                 'locale', 'timezone', 'is_verified', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined', 'is_verified']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name', 'locale', 'timezone']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        attrs.pop('password_confirm')
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'locale', 'timezone', 'profile']
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        instance = super().update(instance, validated_data)
        
        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value
