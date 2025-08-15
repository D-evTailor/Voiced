from rest_framework import serializers
from .onboarding_models import BusinessDashboardConfig, BusinessOnboardingStatus


class BusinessDashboardConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessDashboardConfig
        fields = ['primary_color', 'secondary_color', 'logo_url', 'welcome_message', 
                 'show_booking_widget', 'show_services', 'show_contact_info', 'custom_css']


class BusinessOnboardingStatusSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    next_step = serializers.SerializerMethodField()
    
    class Meta:
        model = BusinessOnboardingStatus
        fields = ['basic_info_completed', 'services_configured', 'business_hours_set', 
                 'vapi_configured', 'first_appointment_received', 'onboarding_completed',
                 'current_step', 'progress_percentage', 'next_step']
        read_only_fields = ['onboarding_completed', 'current_step']
    
    def get_progress_percentage(self, obj):
        completed_steps = sum([
            obj.basic_info_completed,
            obj.services_configured,
            obj.business_hours_set,
            obj.vapi_configured
        ])
        return (completed_steps / 4) * 100
    
    def get_next_step(self, obj):
        if obj.onboarding_completed:
            return None
        
        steps_map = {
            'basic_info': 'Complete business information',
            'services_configured': 'Configure your services',
            'business_hours_set': 'Set business hours',
            'vapi_configured': 'Configure voice assistant'
        }
        
        return steps_map.get(obj.current_step)
