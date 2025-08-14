from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import BaseModel
from apps.core.managers import TenantManager


class Resource(BaseModel):
    RESOURCE_TYPES = [
        ('staff', _('Staff')),
        ('room', _('Room')),
        ('equipment', _('Equipment')),
    ]
    
    name = models.CharField(_('name'), max_length=100)
    type = models.CharField(_('type'), max_length=20, choices=RESOURCE_TYPES)
    description = models.TextField(_('description'), blank=True)
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='resource'
    )
    capacity = models.PositiveIntegerField(_('capacity'), default=1)
    location = models.CharField(_('location'), max_length=100, blank=True)
    color = models.CharField(_('color'), max_length=7, default='#6B7280')
    is_active = models.BooleanField(_('active'), default=True)
    
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
    
    def get_availability_for_date(self, date):
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        day_of_week = date.weekday()
        schedule = self.schedules.filter(
            day_of_week=day_of_week,
            is_active=True,
            effective_from__lte=date
        ).filter(
            models.Q(effective_until__isnull=True) | models.Q(effective_until__gte=date)
        ).first()
        
        if not schedule:
            return {
                'available': False,
                'reason': 'No schedule defined for this day',
                'slots': []
            }
        
        start_datetime = timezone.make_aware(datetime.combine(date, schedule.start_time))
        end_datetime = timezone.make_aware(datetime.combine(date, schedule.end_time))
        
        slots = []
        current_time = start_datetime
        
        while current_time < end_datetime:
            slot_end = current_time + timedelta(minutes=30)
            is_available = not self.has_conflict_at(current_time, slot_end)
            
            slots.append({
                'start': current_time,
                'end': slot_end,
                'available': is_available,
                'conflicts': self.get_conflicts_for_period(current_time, slot_end) if not is_available else []
            })
            
            current_time = slot_end
        
        return {
            'available': any(slot['available'] for slot in slots),
            'schedule': {
                'start': start_datetime,
                'end': end_datetime
            },
            'slots': slots
        }
    
    def has_conflict_at(self, start_time, end_time):
        appointment_conflicts = self.appointment_resources.filter(
            allocated_start__lt=end_time,
            allocated_end__gt=start_time
        ).exists()
        
        if appointment_conflicts:
            return True
        
        block_conflicts = self.blocks.filter(
            start_datetime__lt=end_time,
            end_datetime__gt=start_time,
            deleted_at__isnull=True
        ).exists()
        
        return block_conflicts
    
    def get_conflicts_for_period(self, start_time, end_time):
        conflicts = []
        
        apt_conflicts = self.appointment_resources.filter(
            allocated_start__lt=end_time,
            allocated_end__gt=start_time
        ).select_related('appointment__client', 'appointment__service')
        
        for apt_resource in apt_conflicts:
            conflicts.append({
                'type': 'appointment',
                'start': apt_resource.allocated_start,
                'end': apt_resource.allocated_end,
                'description': f"Appointment: {apt_resource.appointment.get_client_display_name()} - {apt_resource.appointment.service.name}",
                'appointment_id': apt_resource.appointment.id
            })
        
        block_conflicts = self.blocks.filter(
            start_datetime__lt=end_time,
            end_datetime__gt=start_time,
            deleted_at__isnull=True
        )
        
        for block in block_conflicts:
            conflicts.append({
                'type': 'block',
                'start': block.start_datetime,
                'end': block.end_datetime,
                'description': f"{block.get_block_type_display()}: {block.reason}",
                'block_id': block.id
            })
        
        return sorted(conflicts, key=lambda x: x['start'])
    
    def get_next_available_slot(self, duration_minutes, start_from=None):
        from django.utils import timezone
        from datetime import timedelta
        
        if not start_from:
            start_from = timezone.now()
        
        max_date = start_from.date() + timedelta(days=30)
        current_date = start_from.date()
        
        while current_date <= max_date:
            availability = self.get_availability_for_date(current_date)
            
            if availability['available']:
                for i, slot in enumerate(availability['slots']):
                    if not slot['available']:
                        continue
                    
                    consecutive_minutes = 30
                    end_slot_index = i
                    
                    for j in range(i + 1, len(availability['slots'])):
                        next_slot = availability['slots'][j]
                        if not next_slot['available']:
                            break
                        consecutive_minutes += 30
                        end_slot_index = j
                        
                        if consecutive_minutes >= duration_minutes:
                            return {
                                'start': slot['start'],
                                'end': slot['start'] + timedelta(minutes=duration_minutes),
                                'date': current_date
                            }
            
            current_date += timedelta(days=1)
        
        return None
    
    @property
    def utilization_rate(self):
        from django.utils import timezone
        from datetime import timedelta, datetime
        
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        scheduled_appointments = self.appointment_resources.filter(
            allocated_start__gte=month_start,
            allocated_end__lte=month_end,
            appointment__status__in=['confirmed', 'completed', 'in_progress']
        )
        
        total_booked_minutes = sum(
            (apt.allocated_end - apt.allocated_start).total_seconds() / 60
            for apt in scheduled_appointments
        )
        
        working_days = 0
        total_available_minutes = 0
        
        current_date = month_start.date()
        while current_date <= month_end.date():
            day_schedule = self.schedules.filter(
                day_of_week=current_date.weekday(),
                is_active=True
            ).first()
            
            if day_schedule:
                working_days += 1
                daily_minutes = (
                    datetime.combine(current_date, day_schedule.end_time) -
                    datetime.combine(current_date, day_schedule.start_time)
                ).total_seconds() / 60
                total_available_minutes += daily_minutes
            
            current_date += timedelta(days=1)
        
        if total_available_minutes == 0:
            return 0
        
        return min(100, (total_booked_minutes / total_available_minutes) * 100)


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
    
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    day_of_week = models.IntegerField(_('day of week'), choices=DAYS_OF_WEEK)
    start_time = models.TimeField(_('start time'))
    end_time = models.TimeField(_('end time'))
    effective_from = models.DateField(_('effective from'), auto_now_add=True)
    effective_until = models.DateField(_('effective until'), null=True, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    
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
    
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='blocks'
    )
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
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='service_resources'
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='service_resources'
    )
    quantity_required = models.PositiveIntegerField(
        _('quantity required'),
        default=1,
        validators=[MinValueValidator(1)]
    )
    is_required = models.BooleanField(_('required'), default=True)
    preference_order = models.PositiveIntegerField(_('preference order'), default=0)
    
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


class AppointmentResource(models.Model):
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='appointment_resources'
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='appointment_resources'
    )
    allocated_start = models.DateTimeField(_('allocated start'))
    allocated_end = models.DateTimeField(_('allocated end'))
    created_at = models.DateTimeField(auto_now_add=True)
    
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
