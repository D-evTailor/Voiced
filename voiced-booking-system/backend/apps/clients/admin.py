from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['get_display_name', 'email', 'phone', 'business', 'client_segment', 'total_appointments', 'total_spent', 'is_active']
    list_filter = ['business', 'client_segment', 'is_active', 'marketing_consent', 'preferred_language']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['total_appointments', 'completed_appointments', 'cancelled_appointments', 'no_show_appointments', 'total_spent', 'average_spending', 'first_appointment_date', 'last_appointment_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'gender')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'communication_preferences', 'marketing_consent')
        }),
        ('Medical Information', {
            'fields': ('allergies', 'medical_conditions', 'emergency_contact'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_appointments', 'completed_appointments', 'cancelled_appointments', 'no_show_appointments', 'total_spent', 'average_spending', 'first_appointment_date', 'last_appointment_date'),
            'classes': ('collapse',)
        }),
        ('Marketing', {
            'fields': ('source', 'referral_source', 'client_segment', 'loyalty_points'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes', 'internal_notes')
        }),
        ('Status', {
            'fields': ('is_active', 'is_blacklisted', 'blacklist_reason')
        }),
    )
