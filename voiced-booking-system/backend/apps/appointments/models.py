from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from apps.core.mixins import BaseModel
import uuid

class Appointment(BaseModel):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('no_show', _('No Show')),
    ]
    
    SOURCE_CHOICES = [
        ('online', _('Online Booking')),
        ('voice', _('Voice Agent')),
        ('manual', _('Manual Entry')),
        ('phone', _('Phone Call')),
    ]
    
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='appointments')
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    provider = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='provided_appointments')
    customer_name = models.CharField(_('customer name'), max_length=200)
    customer_email = models.EmailField(_('customer email'), validators=[EmailValidator()])
    customer_phone = models.CharField(_('customer phone'), max_length=20, blank=True)
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    source = models.CharField(_('booking source'), max_length=20, choices=SOURCE_CHOICES, default='online')
    notes = models.TextField(_('notes'), blank=True)
    internal_notes = models.TextField(_('internal notes'), blank=True)
    quoted_price = models.DecimalField(_('quoted price'), max_digits=10, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(_('final price'), max_digits=10, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(_('paid amount'), max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        _('payment status'),
        max_length=20,
        choices=[
            ('pending', _('Pending')),
            ('paid', _('Paid')),
            ('partially_paid', _('Partially Paid')),
            ('refunded', _('Refunded')),
            ('failed', _('Failed')),
        ],
        default='pending'
    )
    
    class Meta:
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')
        db_table = 'appointments'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['business', 'start_time']),
            models.Index(fields=['status']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        return f"{self.customer_name} - {self.service.name} ({self.start_time})"
