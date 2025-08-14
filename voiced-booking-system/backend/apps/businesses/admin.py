"""
Django admin configuration for Businesses app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Business, BusinessHours, BusinessMember


class BusinessHoursInline(admin.TabularInline):
    """Inline admin for business hours."""
    model = BusinessHours
    extra = 7  # One for each day of the week
    max_num = 7


class BusinessMemberInline(admin.TabularInline):
    """Inline admin for business members."""
    model = BusinessMember
    extra = 0
    autocomplete_fields = ('user',)


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    """Admin configuration for Business model."""
    
    list_display = (
        'name', 'slug', 'owner', 'email', 'locale', 'is_active',
        'allow_online_booking', 'allow_voice_booking', 'created_at'
    )
    list_filter = (
        'is_active', 'allow_online_booking', 'allow_voice_booking',
        'require_approval', 'locale', 'currency', 'created_at'
    )
    search_fields = ('name', 'slug', 'email', 'owner__email')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'owner', 'description')
        }),
        (_('Contact Information'), {
            'fields': ('email', 'phone', 'website')
        }),
        (_('Address'), {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
        (_('Localization'), {
            'fields': ('locale', 'timezone', 'currency')
        }),
        (_('Settings'), {
            'fields': (
                'is_active', 'allow_online_booking', 'allow_voice_booking',
                'require_approval'
            )
        }),
        (_('Branding'), {
            'fields': ('logo', 'primary_color')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('owner',)
    inlines = [BusinessHoursInline, BusinessMemberInline]


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    """Admin configuration for BusinessHours model."""
    
    list_display = (
        'business', 'get_day_of_week_display', 'open_time', 'close_time', 'is_closed'
    )
    list_filter = ('day_of_week', 'is_closed', 'business')
    search_fields = ('business__name',)
    ordering = ('business', 'day_of_week')
    
    fieldsets = (
        (None, {
            'fields': ('business', 'day_of_week', 'open_time', 'close_time', 'is_closed')
        }),
    )
    
    autocomplete_fields = ('business',)


@admin.register(BusinessMember)
class BusinessMemberAdmin(admin.ModelAdmin):
    """Admin configuration for BusinessMember model."""
    
    list_display = (
        'user', 'business', 'role', 'is_active', 'joined_at'
    )
    list_filter = ('role', 'is_active', 'joined_at')
    search_fields = ('user__email', 'business__name')
    ordering = ('-joined_at',)
    
    fieldsets = (
        (None, {
            'fields': ('business', 'user', 'role', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('joined_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('joined_at', 'updated_at')
    autocomplete_fields = ('business', 'user')
