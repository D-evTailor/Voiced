from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from apps.core.mixins import BaseModel, TimestampMixin
from apps.core.managers import TenantManager
import uuid

class ServiceCategory(BaseModel):
    name = models.CharField(
        _('category name'),
        max_length=100,
        help_text=_('Name of the service category')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Optional description of the category')
    )
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        help_text=_('Order for displaying categories')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True
    )
    class Meta:
        verbose_name = _('Service Category')
        verbose_name_plural = _('Service Categories')
        db_table = 'service_categories'
        unique_together = ['business', 'name']
        ordering = ['business', 'order', 'name']
    def __str__(self):
        return f"{self.business.name} - {self.name}"

class Service(BaseModel):
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services',
        verbose_name=_('category')
    )
    name = models.CharField(
        _('service name'),
        max_length=200,
        help_text=_('Name of the service')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Detailed description of the service')
    )
    duration = models.PositiveIntegerField(
        _('duration (minutes)'),
        validators=[MinValueValidator(5), MaxValueValidator(480)],
        help_text=_('Service duration in minutes')
    )
    buffer_time = models.PositiveIntegerField(
        _('buffer time (minutes)'),
        default=0,
        validators=[MaxValueValidator(60)],
        help_text=_('Buffer time between appointments')
    )
    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_('Service price')
    )
    deposit_required = models.DecimalField(
        _('deposit required'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_('Required deposit amount')
    )
    advance_booking_days = models.PositiveIntegerField(
        _('advance booking days'),
        default=30,
        validators=[MaxValueValidator(365)],
        help_text=_('How many days in advance can this service be booked')
    )
    min_notice_hours = models.PositiveIntegerField(
        _('minimum notice (hours)'),
        default=2,
        validators=[MaxValueValidator(168)],
        help_text=_('Minimum notice required for booking')
    )
    max_attendees = models.PositiveIntegerField(
        _('maximum attendees'),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text=_('Maximum number of people for this service')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Whether this service is available for booking')
    )
    online_booking_enabled = models.BooleanField(
        _('online booking enabled'),
        default=True,
        help_text=_('Allow online booking for this service')
    )
    voice_booking_enabled = models.BooleanField(
        _('voice booking enabled'),
        default=True,
        help_text=_('Allow voice booking for this service')
    )
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        help_text=_('Order for displaying services')
    )
    color = models.CharField(
        _('color'),
        max_length=7,
        default='#3B82F6',
        help_text=_('Color for calendar display (hex code)')
    )
    image = models.ImageField(
        _('service image'),
        upload_to='service_images/',
        blank=True,
        null=True,
        help_text=_('Optional image for the service')
    )
    
    objects = TenantManager()
    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        db_table = 'services'
        ordering = ['business', 'order', 'name']
        indexes = [
            models.Index(fields=['business', 'is_active']),
            models.Index(fields=['category']),
            models.Index(fields=['online_booking_enabled']),
            models.Index(fields=['voice_booking_enabled']),
        ]
    def __str__(self):
        return f"{self.business.name} - {self.name}"
    @property
    def duration_display(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}min"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}min"
    @property
    def total_time_required(self):
        return self.duration + self.buffer_time

class ServiceProvider(TimestampMixin):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='providers',
        verbose_name=_('service')
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='provided_services',
        verbose_name=_('provider')
    )
    is_primary = models.BooleanField(
        _('primary provider'),
        default=False,
        help_text=_('Primary provider for this service')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True
    )
    class Meta:
        verbose_name = _('Service Provider')
        verbose_name_plural = _('Service Providers')
        db_table = 'service_providers'
        unique_together = ['service', 'user']
        ordering = ['service', '-is_primary', 'user']
    def __str__(self):
        primary = " (Primary)" if self.is_primary else ""
        return f"{self.user.get_full_name()} - {self.service.name}{primary}"
