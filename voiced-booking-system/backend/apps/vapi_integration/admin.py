from django.contrib import admin
from .models import VapiConfig, VapiCallLog


@admin.register(VapiConfig)
class VapiConfigAdmin(admin.ModelAdmin):
    list_display = ['business', 'assistant_name', 'language', 'is_active']
    list_filter = ['language', 'is_active']
    search_fields = ['business__name', 'assistant_name']
    ordering = ['business']


@admin.register(VapiCallLog)
class VapiCallLogAdmin(admin.ModelAdmin):
    list_display = ['business', 'vapi_call_id', 'caller_phone', 'call_status', 'booking_successful', 'created_at']
    list_filter = ['call_status', 'booking_successful', 'business']
    search_fields = ['vapi_call_id', 'caller_phone', 'business__name']
    ordering = ['-created_at']
