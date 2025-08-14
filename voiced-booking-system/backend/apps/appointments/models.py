from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from apps.core.mixins import BaseModel
from apps.core.utils import generate_unique_reference
from decimal import Decimal
import uuid

class Appointment(BaseModel):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('no_show', _('No Show')),
        ('rescheduled', _('Rescheduled')),
    ]
    
    SOURCE_CHOICES = [
        ('online', _('Online Booking')),
        ('voice_agent', _('Voice Agent')),
        ('manual', _('Manual Entry')),
        ('phone_call', _('Phone Call')),
        ('walk_in', _('Walk In')),
        ('mobile_app', _('Mobile App')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('partially_paid', _('Partially Paid')),
        ('refunded', _('Refunded')),
        ('failed', _('Failed')),
        ('waived', _('Waived')),
    ]
    
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('service')
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('client'),
        null=True,
        blank=True
    )
    provider = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='provided_appointments',
        verbose_name=_('service provider')
    )
    
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    actual_start_time = models.DateTimeField(_('actual start time'), null=True, blank=True)
    actual_end_time = models.DateTimeField(_('actual end time'), null=True, blank=True)
    
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    status_changed_at = models.DateTimeField(_('status changed at'), auto_now_add=True)
    status_changed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='status_changed_appointments',
        verbose_name=_('status changed by')
    )
    
    source = models.CharField(_('booking source'), max_length=20, choices=SOURCE_CHOICES, default='online')
    booking_reference = models.CharField(_('booking reference'), max_length=50, unique=True, blank=True)
    
    quoted_price = models.DecimalField(_('quoted price'), max_digits=10, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(_('final price'), max_digits=10, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(_('paid amount'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_status = models.CharField(_('payment status'), max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    confirmation_sent_at = models.DateTimeField(_('confirmation sent at'), null=True, blank=True)
    reminder_sent_at = models.DateTimeField(_('reminder sent at'), null=True, blank=True)
    
    client_notes = models.TextField(_('client notes'), blank=True)
    staff_notes = models.TextField(_('staff notes'), blank=True)
    cancellation_reason = models.TextField(_('cancellation reason'), blank=True)
    
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
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
            models.CheckConstraint(
                check=models.Q(paid_amount__gte=0),
                name='appointment_paid_amount_non_negative'
            ),
        ]
        
        indexes = [
            models.Index(fields=['business', 'start_time']),
            models.Index(fields=['business', 'status', 'start_time']),
            models.Index(fields=['client', 'start_time']),
            models.Index(fields=['service', 'start_time']),
            models.Index(fields=['provider', 'start_time']),
            models.Index(fields=['status', 'start_time']),
            models.Index(fields=['source']),
            models.Index(fields=['booking_reference']),
        ]
    
    def __str__(self):
        client_name = self.get_client_display_name()
        return f"{client_name} - {self.service.name} ({self.start_time})"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        super().save(*args, **kwargs)
    
    def generate_booking_reference(self):
        return generate_unique_reference(
            self.business.slug[:3].upper(),
            self.start_time,
            5
        )
    
    @property
    def duration_minutes(self):
        if self.actual_start_time and self.actual_end_time:
            delta = self.actual_end_time - self.actual_start_time
        else:
            delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
    
    @property
    def is_confirmed(self):
        return self.status in ['confirmed', 'in_progress', 'completed']
    
    @property
    def can_cancel(self):
        if self.status in ['completed', 'cancelled', 'no_show']:
            return False
        
        cancellation_hours = getattr(self.service, 'cancellation_policy_hours', 24)
        cutoff_time = self.start_time - timezone.timedelta(hours=cancellation_hours)
        
        return timezone.now() < cutoff_time
    
    @property
    def remaining_balance(self):
        if not self.final_price:
            return Decimal('0.00')
        return max(Decimal('0.00'), self.final_price - self.paid_amount)
    
    def get_client_display_name(self):
        if self.client:
            return self.client.get_display_name()
        return self.customer_name or 'Unknown Client'
    
    def get_client_email(self):
        if self.client:
            return self.client.email
        return self.customer_email
    
    def get_client_phone(self):
        if self.client:
            return self.client.phone
        return self.customer_phone
    
    @property
    def customer_display_name(self):
        return self.get_client_display_name()
    
    @property
    def customer_contact_email(self):
        return self.get_client_email()
    
    @property
    def customer_contact_phone(self):
        return self.get_client_phone()
