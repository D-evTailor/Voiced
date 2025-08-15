from django.contrib import admin
from .models import VapiConfiguration, VapiCall, VapiCallTranscript, VapiCallAnalysis, VapiAppointmentIntegration, VapiUsageMetrics


@admin.register(VapiConfiguration)
class VapiConfigurationAdmin(admin.ModelAdmin):
    list_display = ['business', 'assistant_name', 'language', 'is_active', 'created_at']
    list_filter = ['is_active', 'language', 'voice_provider', 'model_provider', 'created_at']
    search_fields = ['business__name', 'assistant_name', 'assistant_id', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Business Configuration', {
            'fields': ('business', 'is_active')
        }),
        ('Assistant Settings', {
            'fields': ('assistant_id', 'assistant_name', 'language', 'first_message', 'system_prompt')
        }),
        ('Phone Configuration', {
            'fields': ('phone_number_id', 'phone_number')
        }),
        ('Voice & Model', {
            'fields': ('voice_provider', 'voice_id', 'model_provider', 'model_name')
        }),
        ('Server Configuration', {
            'fields': ('server_url', 'server_secret', 'webhook_timeout')
        }),
        ('Call Settings', {
            'fields': ('max_duration_seconds', 'silence_timeout_seconds', 'response_delay_seconds')
        }),
        ('Advanced', {
            'fields': ('is_shared_agent', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class VapiCallTranscriptInline(admin.StackedInline):
    model = VapiCallTranscript
    extra = 0
    readonly_fields = ('transcript', 'messages')


class VapiCallAnalysisInline(admin.StackedInline):
    model = VapiCallAnalysis
    extra = 0
    readonly_fields = ('summary', 'structured_data', 'success_evaluation')


class VapiAppointmentIntegrationInline(admin.StackedInline):
    model = VapiAppointmentIntegration
    extra = 0
    readonly_fields = ('booking_successful', 'booking_error', 'extracted_data')


@admin.register(VapiCall)
class VapiCallAdmin(admin.ModelAdmin):
    list_display = ['business', 'call_id', 'customer_number', 'status', 'cost', 'duration_display', 'started_at']
    list_filter = ['status', 'type', 'ended_reason', 'phone_call_provider', 'created_at']
    search_fields = ['call_id', 'customer_number', 'phone_number', 'business__name']
    readonly_fields = ['call_id', 'org_id', 'created_at', 'updated_at', 'duration_display']
    inlines = [VapiCallTranscriptInline, VapiCallAnalysisInline, VapiAppointmentIntegrationInline]
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('business')
    
    def duration_display(self, obj):
        duration = obj.duration_seconds
        if duration:
            minutes, seconds = divmod(duration, 60)
            return f"{minutes}m {seconds}s"
        return "-"
    duration_display.short_description = 'Duration'


@admin.register(VapiUsageMetrics)
class VapiUsageMetricsAdmin(admin.ModelAdmin):
    list_display = ['business', 'date', 'total_calls', 'total_minutes', 'successful_bookings', 'estimated_cost']
    list_filter = ['date', 'created_at']
    search_fields = ['business__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('business')
