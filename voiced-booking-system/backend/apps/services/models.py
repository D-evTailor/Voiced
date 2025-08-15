from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from apps.core.mixins import BaseModel, BaseFieldsMixin, OrderMixin, BusinessStatsMixin, TimeCalculationMixin
from apps.core.managers import TenantManager


class ServiceCategory(BaseModel, OrderMixin, BusinessStatsMixin):
    name = models.CharField(_('category name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    _count_relation = 'services'
    
    class Meta:
        verbose_name = _('Service Category')
        verbose_name_plural = _('Service Categories')
        db_table = 'service_categories'
        unique_together = ['business', 'name']
        ordering = ['business', 'order', 'name']
    
    def __str__(self):
        return f"{self.business.name} - {self.name}"


class Service(BaseModel, OrderMixin, TimeCalculationMixin, BusinessStatsMixin):
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='services')
    name = models.CharField(_('service name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    duration = models.PositiveIntegerField(_('duration (minutes)'), validators=[MinValueValidator(5), MaxValueValidator(480)])
    buffer_time = models.PositiveIntegerField(_('buffer time (minutes)'), default=0, validators=[MaxValueValidator(60)])
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    max_attendees = models.PositiveIntegerField(_('maximum attendees'), default=1, validators=[MinValueValidator(1), MaxValueValidator(100)])
    online_booking_enabled = models.BooleanField(_('online booking enabled'), default=True)
    voice_booking_enabled = models.BooleanField(_('voice booking enabled'), default=True)
    resources = models.ManyToManyField('resources.Resource', through='resources.ServiceResource', related_name='services')
    _count_relation = 'providers'
    
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


class ServiceProvider(BaseFieldsMixin):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='providers')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='provided_services')
    is_primary = models.BooleanField(_('primary provider'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('Service Provider')
        verbose_name_plural = _('Service Providers')
        db_table = 'service_providers'
        unique_together = ['service', 'user']
        ordering = ['service', '-is_primary', 'user']
    
    def __str__(self):
        return f"{self.service.name} - {self.user.get_full_name()}"
