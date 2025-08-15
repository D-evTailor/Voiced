from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import BaseModel, BaseFieldsMixin
from apps.core.managers import TenantManager
from apps.core.utils import RESOURCE_TYPE_CHOICES


class Resource(BaseModel):
    name = models.CharField(_('name'), max_length=100)
    type = models.CharField(_('type'), max_length=20, choices=RESOURCE_TYPE_CHOICES)
    description = models.TextField(_('description'), blank=True)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, null=True, blank=True, related_name='resource')
    capacity = models.PositiveIntegerField(_('capacity'), default=1)
    location = models.CharField(_('location'), max_length=100, blank=True)
    color = models.CharField(_('color'), max_length=7, default='#6B7280')
    
    objects = TenantManager()
    
    class Meta:
        verbose_name = _('Resource')
        verbose_name_plural = _('Resources')
        db_table = 'resources'
        unique_together = ['business', 'name']
        indexes = [
            models.Index(fields=['business', 'type', 'is_active']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.business.name} - {self.name}"


class ResourceSchedule(BaseModel):
    DAYS_OF_WEEK = [
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ]
    
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(_('day of week'), choices=DAYS_OF_WEEK)
    start_time = models.TimeField(_('start time'))
    end_time = models.TimeField(_('end time'))
    effective_from = models.DateField(_('effective from'), auto_now_add=True)
    effective_until = models.DateField(_('effective until'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Resource Schedule')
        verbose_name_plural = _('Resource Schedules')
        db_table = 'resource_schedules'
        unique_together = ['resource', 'day_of_week', 'effective_from']
        indexes = [
            models.Index(fields=['resource', 'day_of_week', 'is_active']),
            models.Index(fields=['effective_from', 'effective_until']),
        ]
    
    def __str__(self):
        day_name = self.get_day_of_week_display()
        return f"{self.resource.name} - {day_name}: {self.start_time}-{self.end_time}"


class ResourceBlock(BaseModel):
    BLOCK_TYPES = [
        ('vacation', _('Vacation')),
        ('sick_leave', _('Sick Leave')),
        ('maintenance', _('Maintenance')),
        ('break', _('Break')),
        ('training', _('Training')),
        ('other', _('Other')),
    ]
    
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='blocks')
    start_datetime = models.DateTimeField(_('start datetime'))
    end_datetime = models.DateTimeField(_('end datetime'))
    block_type = models.CharField(_('block type'), max_length=20, choices=BLOCK_TYPES)
    reason = models.TextField(_('reason'), blank=True)
    is_recurring = models.BooleanField(_('recurring'), default=False)
    recurrence_rule = models.JSONField(_('recurrence rule'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Resource Block')
        verbose_name_plural = _('Resource Blocks')
        db_table = 'resource_blocks'
        indexes = [
            models.Index(fields=['resource', 'start_datetime', 'end_datetime']),
            models.Index(fields=['block_type']),
        ]
    
    def __str__(self):
        return f"{self.resource.name} - {self.get_block_type_display()}: {self.start_datetime}"


class ServiceResource(models.Model):
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='service_resources')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='service_resources')
    quantity_required = models.PositiveIntegerField(_('quantity required'), default=1, validators=[MinValueValidator(1)])
    is_required = models.BooleanField(_('required'), default=True)
    preference_order = models.PositiveIntegerField(_('preference order'), default=0)
    setup_time = models.PositiveIntegerField(_('setup minutes'), default=0)
    cleanup_time = models.PositiveIntegerField(_('cleanup minutes'), default=0)
    
    class Meta:
        verbose_name = _('Service Resource')
        verbose_name_plural = _('Service Resources')
        db_table = 'service_resources'
        unique_together = ['service', 'resource']
        indexes = [
            models.Index(fields=['service', 'is_required']),
            models.Index(fields=['resource']),
        ]
    
    def __str__(self):
        return f"{self.service.name} -> {self.resource.name} (x{self.quantity_required})"


class AppointmentResource(BaseFieldsMixin):
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE, related_name='appointment_resources')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='appointment_resources')
    allocated_start = models.DateTimeField(_('allocated start'))
    allocated_end = models.DateTimeField(_('allocated end'))
    
    class Meta:
        verbose_name = _('Appointment Resource')
        verbose_name_plural = _('Appointment Resources')
        db_table = 'appointment_resources'
        indexes = [
            models.Index(fields=['resource', 'allocated_start', 'allocated_end']),
            models.Index(fields=['appointment']),
        ]
    
    def __str__(self):
        return f"{self.appointment} -> {self.resource.name}"
