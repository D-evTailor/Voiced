from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from apps.core.mixins import BaseModel, ClientStatsMixin
from apps.core.utils import generate_unique_reference
from apps.core.choices import APPOINTMENT_STATUS_CHOICES, APPOINTMENT_SOURCE_CHOICES, PAYMENT_STATUS_CHOICES


class Appointment(BaseModel, ClientStatsMixin):
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='appointments')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    resources = models.ManyToManyField('resources.Resource', through='resources.AppointmentResource', related_name='appointments')
    
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    status = models.CharField(_('status'), max_length=20, choices=APPOINTMENT_STATUS_CHOICES, default='pending')
    source = models.CharField(_('booking source'), max_length=20, choices=APPOINTMENT_SOURCE_CHOICES, default='online')
    booking_reference = models.CharField(_('booking reference'), max_length=50, unique=True, blank=True)
    
    quoted_price = models.DecimalField(_('quoted price'), max_digits=10, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(_('final price'), max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(_('payment status'), max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    client_notes = models.TextField(_('client notes'), blank=True)
    staff_notes = models.TextField(_('staff notes'), blank=True)
    special_requirements = models.TextField(_('special requirements'), blank=True)
    
    is_recurring = models.BooleanField(_('recurring'), default=False)
    recurrence_rule = models.JSONField(_('recurrence rule'), default=dict, blank=True)
    parent_appointment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='recurring_appointments')
    group_size = models.PositiveIntegerField(_('group size'), default=1)
    
    customer_name = models.CharField(_('customer name'), max_length=200, blank=True)
    customer_email = models.EmailField(_('customer email'), validators=[EmailValidator()], blank=True)
    customer_phone = models.CharField(_('customer phone'), max_length=20, blank=True)
    
    class Meta:
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')
        db_table = 'appointments'
        ordering = ['-start_time']
        
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='appointment_end_after_start'
            ),
        ]
        
        indexes = [
            models.Index(fields=['business', 'start_time']),
            models.Index(fields=['business', 'status', 'start_time']),
            models.Index(fields=['client', 'start_time']),
            models.Index(fields=['service', 'start_time']),
            models.Index(fields=['status', 'start_time']),
            models.Index(fields=['source']),
            models.Index(fields=['booking_reference']),
            models.Index(fields=['is_recurring']),
            models.Index(fields=['parent_appointment']),
        ]
    
    def __str__(self):
        client_name = self.get_client_display_name()
        return f"{client_name} - {self.service.name} ({self.start_time})"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        
        if not self.end_time and self.start_time and self.service:
            from datetime import timedelta
            self.end_time = self.start_time + timedelta(minutes=self.service.duration)
        
        super().save(*args, **kwargs)
        
        if self.status in ['completed', 'confirmed']:
            self.update_client_stats()
    
    def generate_booking_reference(self):
        return generate_unique_reference(
            self.business.slug[:3].upper(),
            self.start_time,
            5
        )
    
    def get_client_display_name(self):
        if self.client:
            return self.client.get_display_name()
        return self.customer_name or 'Unknown Client'
