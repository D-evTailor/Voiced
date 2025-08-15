from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.mixins import BaseModel, SimpleModel
from apps.core.choices import VAPI_CALL_STATUS_CHOICES, VAPI_CALL_TYPE_CHOICES, VAPI_ENDED_REASON_CHOICES, LANGUAGE_CHOICES
from .optimizations import VapiConfigManager, VapiCacheKeys


class VapiConfiguration(BaseModel):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='vapi_configurations')
    phone_number_id = models.CharField(_('phone number ID'), max_length=255, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    assistant_id = models.CharField(_('assistant ID'), max_length=255, blank=True)
    assistant_name = models.CharField(_('assistant name'), max_length=100, default='Booking Assistant')
    language = models.CharField(_('language'), max_length=10, choices=LANGUAGE_CHOICES, default='es')
    server_url = models.URLField(_('server URL'))
    server_secret = models.CharField(_('server secret'), max_length=255, blank=True)
    webhook_timeout = models.IntegerField(
        _('webhook timeout (ms)'), 
        default=7500,
        validators=[MinValueValidator(1000), MaxValueValidator(30000)]
    )
    voice_provider = models.CharField(_('voice provider'), max_length=50, default='openai')
    voice_id = models.CharField(_('voice ID'), max_length=100, default='nova')
    model_provider = models.CharField(_('model provider'), max_length=50, default='openai')
    model_name = models.CharField(_('model name'), max_length=100, default='gpt-4o-mini')
    first_message = models.TextField(_('first message'), blank=True)
    system_prompt = models.TextField(_('system prompt'), blank=True)
    max_duration_seconds = models.IntegerField(_('max duration seconds'), default=1800)
    silence_timeout_seconds = models.IntegerField(_('silence timeout seconds'), default=30)
    response_delay_seconds = models.FloatField(_('response delay seconds'), default=0.4)
    is_shared_agent = models.BooleanField(_('is shared agent'), default=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Vapi Configuration')
        verbose_name_plural = _('Vapi Configurations')
        db_table = 'vapi_configurations'
        constraints = [
            models.UniqueConstraint(
                fields=['business'], 
                condition=models.Q(is_active=True),
                name='unique_active_config_per_business'
            ),
            models.UniqueConstraint(
                fields=['phone_number_id'],
                condition=models.Q(phone_number_id__isnull=False),
                name='unique_phone_number_id'
            )
        ]
        indexes = [
            models.Index(fields=['business', 'is_active']),
            models.Index(fields=['phone_number_id']),
            models.Index(fields=['assistant_id']),
            models.Index(fields=['is_shared_agent']),
        ]
    
    def __str__(self):
        return f"{self.business.name} - Vapi Config {'(Shared)' if self.is_shared_agent else ''}"
    
    def save(self, *args, **kwargs):
        if self.is_shared_agent and not self.metadata:
            self.metadata = {
                'tenant_id': str(self.business.id),
                'business_name': self.business.name,
                'business_slug': self.business.slug
            }
        super().save(*args, **kwargs)
        VapiConfigManager.invalidate_business_cache(self.business_id)
    
    def delete(self, *args, **kwargs):
        business_id = self.business_id
        super().delete(*args, **kwargs)
        VapiConfigManager.invalidate_business_cache(business_id)
    
    @property
    def assistant_config(self):
        return {
            'firstMessage': self.first_message or f'Hola, soy el asistente de {self.business.name}. ¿En qué puedo ayudarte?',
            'voice': {'provider': self.voice_provider, 'voiceId': self.voice_id},
            'model': {'provider': self.model_provider, 'model': self.model_name},
            'serverUrl': self.server_url,
            'serverUrlSecret': self.server_secret,
            'maxDurationSeconds': self.max_duration_seconds,
            'silenceTimeoutSeconds': self.silence_timeout_seconds,
            'responseDelaySeconds': self.response_delay_seconds,
        }


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
    assistant_id = models.CharField(_('assistant ID'), max_length=255, blank=True)
    squad_id = models.CharField(_('squad ID'), max_length=255, blank=True)
    phone_call_provider = models.CharField(_('phone call provider'), max_length=50, blank=True)
    phone_call_transport = models.CharField(_('phone call transport'), max_length=50, blank=True)
    
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
            models.Index(fields=['assistant_id']),
            models.Index(fields=['started_at']),
            models.Index(fields=['ended_at']),
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


class VapiUsageMetrics(models.Model):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='vapi_usage')
    date = models.DateField(_('date'))
    total_calls = models.PositiveIntegerField(_('total calls'), default=0)
    total_minutes = models.DecimalField(_('total minutes'), max_digits=10, decimal_places=2, default=0)
    total_function_calls = models.PositiveIntegerField(_('total function calls'), default=0)
    successful_bookings = models.PositiveIntegerField(_('successful bookings'), default=0)
    failed_bookings = models.PositiveIntegerField(_('failed bookings'), default=0)
    estimated_cost = models.DecimalField(_('estimated cost'), max_digits=10, decimal_places=4, default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Vapi Usage Metrics')
        verbose_name_plural = _('Vapi Usage Metrics')
        db_table = 'vapi_usage_metrics'
        unique_together = ['business', 'date']
        indexes = [
            models.Index(fields=['business', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.business.name} - {self.date}: {self.total_calls} calls"
