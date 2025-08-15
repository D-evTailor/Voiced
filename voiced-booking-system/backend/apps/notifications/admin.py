from django.contrib import admin
from .models import NotificationTemplate, Notification


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'business', 'type', 'channel', 'is_active', 'is_system_default']
    list_filter = ['type', 'channel', 'is_active', 'is_system_default']
    search_fields = ['name', 'business__name']
    ordering = ['business', 'type', 'channel']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient_email', 'channel', 'status', 'sent_at', 'created_at']
    list_filter = ['channel', 'status', 'recipient_type']
    search_fields = ['recipient_email', 'recipient_phone', 'subject']
    ordering = ['-created_at']
