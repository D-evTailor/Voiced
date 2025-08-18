from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['get_display_name', 'email', 'phone', 'business', 'total_appointments', 'total_spent', 'is_active']
    list_filter = ['business', 'is_active', 'marketing_consent', 'preferred_language']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['total_appointments', 'total_spent', 'last_appointment_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'date_of_birth')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'marketing_consent', 'preferred_staff')
        }),
        ('Statistics', {
            'fields': ('total_appointments', 'total_spent', 'last_appointment_date'),
            'classes': ('collapse',)
        }),
        ('Voice Recognition', {
            'fields': ('voice_recognition_id',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
