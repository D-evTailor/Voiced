from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import BaseModel, SimpleModel
from apps.core.choices import VAPI_CALL_STATUS_CHOICES, VAPI_CALL_TYPE_CHOICES, VAPI_ENDED_REASON_CHOICES, LANGUAGE_CHOICES
from .cache_manager import VapiCacheManager


class VapiConfiguration(BaseModel):
    phone_number_id = models.CharField(_('phone number ID'), max_length=255, blank=True)
    assistant_id = models.CharField(_('assistant ID'), max_length=255)
    assistant_name = models.CharField(_('assistant name'), max_length=100, default='Booking Assistant')
    language = models.CharField(_('language'), max_length=10, choices=LANGUAGE_CHOICES, default='es')
    server_url = models.URLField(_('server URL'), blank=True)
    server_secret = models.CharField(_('server secret'), max_length=255, blank=True)
    
    class Meta:
        verbose_name = _('Vapi Configuration')
        verbose_name_plural = _('Vapi Configurations')
        db_table = 'vapi_configurations'
        indexes = [
            models.Index(fields=['business', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.business.name} - Vapi Config"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        VapiCacheManager.invalidate_config_cache(self.business_id)
    
    def delete(self, *args, **kwargs):
        business_id = self.business_id
        super().delete(*args, **kwargs)
        VapiCacheManager.invalidate_config_cache(business_id)


class VapiCall(SimpleModel):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='vapi_calls')
    call_id = models.CharField(_('call ID'), max_length=255, unique=True)
    org_id = models.CharField(_('org ID'), max_length=255, blank=True)
    type = models.CharField(_('type'), max_length=30, choices=VAPI_CALL_TYPE_CHOICES, blank=True)
    status = models.CharField(_('status'), max_length=20, choices=VAPI_CALL_STATUS_CHOICES, default='scheduled')
    ended_reason = models.CharField(_('ended reason'), max_length=100, choices=VAPI_ENDED_REASON_CHOICES, blank=True)
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    ended_at = models.DateTimeField(_('ended at'), null=True, blank=True)
    cost = models.DecimalField(_('cost'), max_digits=8, decimal_places=4, null=True, blank=True)
    cost_breakdown = models.JSONField(_('cost breakdown'), default=dict, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    customer_number = models.CharField(_('customer number'), max_length=20, blank=True)
    
    class Meta:
        verbose_name = _('Vapi Call')
        verbose_name_plural = _('Vapi Calls')
        db_table = 'vapi_calls'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business', 'created_at']),
            models.Index(fields=['call_id']),
            models.Index(fields=['status']),
            models.Index(fields=['customer_number']),
        ]
    
    def __str__(self):
        return f"{self.business.name} - {self.call_id} ({self.status})"
    
    @property
    def duration_seconds(self):
        if self.started_at and self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds())
        return None


class VapiCallTranscript(models.Model):
    call = models.OneToOneField(VapiCall, on_delete=models.CASCADE, related_name='transcript')
    transcript = models.TextField(_('transcript'), blank=True)
    messages = models.JSONField(_('messages'), default=list, blank=True)
    
    class Meta:
        verbose_name = _('Vapi Call Transcript')
        verbose_name_plural = _('Vapi Call Transcripts')
        db_table = 'vapi_call_transcripts'
    
    def __str__(self):
        return f"Transcript for {self.call.call_id}"


class VapiCallAnalysis(models.Model):
    call = models.OneToOneField(VapiCall, on_delete=models.CASCADE, related_name='analysis')
    summary = models.TextField(_('summary'), blank=True)
    structured_data = models.JSONField(_('structured data'), default=dict, blank=True)
    success_evaluation = models.TextField(_('success evaluation'), blank=True)
    
    class Meta:
        verbose_name = _('Vapi Call Analysis')
        verbose_name_plural = _('Vapi Call Analyses')
        db_table = 'vapi_call_analyses'
    
    def __str__(self):
        return f"Analysis for {self.call.call_id}"


class VapiAppointmentIntegration(models.Model):
    call = models.OneToOneField(VapiCall, on_delete=models.CASCADE, related_name='appointment_integration')
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE, related_name='vapi_integration')
    booking_successful = models.BooleanField(_('booking successful'), default=False)
    booking_error = models.TextField(_('booking error'), blank=True)
    extracted_data = models.JSONField(_('extracted data'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Vapi Appointment Integration')
        verbose_name_plural = _('Vapi Appointment Integrations')
        db_table = 'vapi_appointment_integrations'
        indexes = [
            models.Index(fields=['booking_successful']),
        ]
    
    def __str__(self):
        return f"{self.call.call_id} -> {self.appointment.id if self.appointment else 'No appointment'}"
