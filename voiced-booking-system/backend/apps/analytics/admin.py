from django.contrib import admin
from .models import BusinessMetrics, AuditLog


@admin.register(BusinessMetrics)
class BusinessMetricsAdmin(admin.ModelAdmin):
    list_display = ['business', 'metric_date', 'metric_type', 'total_appointments', 'revenue_total']
    list_filter = ['metric_type', 'business']
    search_fields = ['business__name']
    ordering = ['-metric_date']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'table_name', 'user_email', 'created_at']
    list_filter = ['action', 'table_name', 'business']
    search_fields = ['user_email', 'table_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'old_values', 'new_values']
