from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import BaseModel, UUIDMixin, TimestampMixin
from apps.core.utils import get_vapi_context_for_business_type


class VapiConfiguration(BaseModel):
    vapi_phone_number = models.CharField(_('vapi phone number'), max_length=20, blank=True)
    assistant_id = models.CharField(_('Vapi assistant ID'), max_length=255)
    assistant_name = models.CharField(_('assistant name'), max_length=100, default='Booking Assistant')
    assistant_greeting = models.TextField(_('assistant greeting'), blank=True)
    language = models.CharField(
        _('language'),
        max_length=10,
        choices=[
            ('es', _('Spanish')),
            ('en', _('English')),
        ],
        default='es'
    )
    business_context = models.TextField(_('business context'), blank=True)
    settings = models.JSONField(_('settings'), default=dict, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('Vapi Configuration')
        verbose_name_plural = _('Vapi Configurations')
        db_table = 'vapi_configurations'
        indexes = [
            models.Index(fields=['business', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.business.name} - Vapi Config"
    
    def get_context_for_business_type(self):
        return get_vapi_context_for_business_type(self.business.business_type)


class VapiCallLog(UUIDMixin, TimestampMixin):
    CALL_STATUS_CHOICES = [
        ('initiated', _('Initiated')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]
    
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='vapi_call_logs')
    vapi_call_id = models.CharField(_('vapi call ID'), max_length=100, unique=True)
    caller_phone = models.CharField(_('caller phone'), max_length=20, blank=True)
    call_duration_seconds = models.PositiveIntegerField(_('call duration seconds'), null=True, blank=True)
    call_status = models.CharField(_('call status'), max_length=20, choices=CALL_STATUS_CHOICES, default='initiated')
    transcript = models.TextField(_('transcript'), blank=True)
    summary = models.TextField(_('summary'), blank=True)
    intent_detected = models.CharField(_('intent detected'), max_length=100, blank=True)
    entities_extracted = models.JSONField(_('entities extracted'), default=dict, blank=True)
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vapi_call_logs'
    )
    booking_successful = models.BooleanField(_('booking successful'), default=False)
    booking_error = models.TextField(_('booking error'), blank=True)
    call_started_at = models.DateTimeField(_('call started at'), null=True, blank=True)
    call_ended_at = models.DateTimeField(_('call ended at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Vapi Call Log')
        verbose_name_plural = _('Vapi Call Logs')
        db_table = 'vapi_call_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business', 'created_at']),
            models.Index(fields=['vapi_call_id']),
            models.Index(fields=['booking_successful']),
        ]
    
    def __str__(self):
        return f"{self.business.name} - Call {self.vapi_call_id} ({self.call_status})"
