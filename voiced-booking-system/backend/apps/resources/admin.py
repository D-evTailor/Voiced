from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Resource, ResourceSchedule, ResourceBlock, ServiceResource, AppointmentResource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'business', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'business']
    search_fields = ['name', 'business__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('business', 'name', 'type', 'description')
        }),
        (_('Details'), {
            'fields': ('user', 'capacity', 'location', 'color')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ResourceSchedule)
class ResourceScheduleAdmin(admin.ModelAdmin):
    list_display = ['resource', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']
    search_fields = ['resource__name']


@admin.register(ResourceBlock)
class ResourceBlockAdmin(admin.ModelAdmin):
    list_display = ['resource', 'block_type', 'start_datetime', 'end_datetime']
    list_filter = ['block_type', 'is_recurring']
    search_fields = ['resource__name', 'reason']


@admin.register(ServiceResource)
class ServiceResourceAdmin(admin.ModelAdmin):
    list_display = ['service', 'resource', 'quantity_required', 'is_required']
    list_filter = ['is_required']
    search_fields = ['service__name', 'resource__name']


@admin.register(AppointmentResource)
class AppointmentResourceAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'resource', 'allocated_start', 'allocated_end']
    search_fields = ['appointment__customer_name', 'resource__name']
