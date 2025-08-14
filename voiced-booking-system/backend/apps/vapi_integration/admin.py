from django.contrib import admin
from .models import VapiConfig, VapiCallLog


@admin.register(VapiConfig)
class VapiConfigAdmin(admin.ModelAdmin):
    list_display = ['business', 'assistant_name', 'language', 'is_active']
    list_filter = ['language', 'is_active']
    search_fields = ['business__name', 'assistant_name']
    ordering = ['business']


from django.contrib import admin
from .models import VapiConfiguration, VapiCall, VapiCallTranscript, VapiCallAnalysis, VapiAppointmentIntegration


@admin.register(VapiConfiguration)
class VapiConfigurationAdmin(admin.ModelAdmin):
    list_display = ['business', 'assistant_name', 'language', 'is_active', 'created_at']
    list_filter = ['is_active', 'language', 'created_at']
    search_fields = ['business__name', 'assistant_name', 'assistant_id']
    readonly_fields = ['created_at', 'updated_at']


class VapiCallTranscriptInline(admin.StackedInline):
    model = VapiCallTranscript
    extra = 0


class VapiCallAnalysisInline(admin.StackedInline):
    model = VapiCallAnalysis
    extra = 0


class VapiAppointmentIntegrationInline(admin.StackedInline):
    model = VapiAppointmentIntegration
    extra = 0


@admin.register(VapiCall)
class VapiCallAdmin(admin.ModelAdmin):
    list_display = ['business', 'call_id', 'customer_number', 'status', 'cost', 'started_at', 'ended_at']
    list_filter = ['status', 'type', 'ended_reason', 'created_at']
    search_fields = ['call_id', 'customer_number', 'business__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [VapiCallTranscriptInline, VapiCallAnalysisInline, VapiAppointmentIntegrationInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('business')


@admin.register(VapiCallTranscript)
class VapiCallTranscriptAdmin(admin.ModelAdmin):
    list_display = ['call', 'created_at']
    search_fields = ['call__call_id', 'transcript']
    readonly_fields = ['created_at']


@admin.register(VapiCallAnalysis)
class VapiCallAnalysisAdmin(admin.ModelAdmin):
    list_display = ['call', 'summary', 'created_at']
    search_fields = ['call__call_id', 'summary']
    readonly_fields = ['created_at']


@admin.register(VapiAppointmentIntegration)
class VapiAppointmentIntegrationAdmin(admin.ModelAdmin):
    list_display = ['call', 'appointment', 'booking_successful']
    list_filter = ['booking_successful']
    search_fields = ['call__call_id', 'appointment__id']
