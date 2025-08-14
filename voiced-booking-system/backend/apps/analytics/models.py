from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import UUIDMixin, TimestampMixin, BaseModel
from decimal import Decimal


class BusinessMetrics(BaseModel):
    METRIC_TYPES = [
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
    ]
    
    metric_date = models.DateField(_('metric date'))
    metric_type = models.CharField(_('metric type'), max_length=50, choices=METRIC_TYPES, default='daily')
    total_appointments = models.PositiveIntegerField(_('total appointments'), default=0)
    completed_appointments = models.PositiveIntegerField(_('completed appointments'), default=0)
    cancelled_appointments = models.PositiveIntegerField(_('cancelled appointments'), default=0)
    no_show_appointments = models.PositiveIntegerField(_('no show appointments'), default=0)
    revenue_total = models.DecimalField(
        _('total revenue'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    revenue_average_per_appointment = models.DecimalField(
        _('average revenue per appointment'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    new_clients = models.PositiveIntegerField(_('new clients'), default=0)
    returning_clients = models.PositiveIntegerField(_('returning clients'), default=0)
    staff_utilization_percentage = models.DecimalField(
        _('staff utilization percentage'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    room_utilization_percentage = models.DecimalField(
        _('room utilization percentage'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    custom_metrics = models.JSONField(_('custom metrics'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Business Metrics')
        verbose_name_plural = _('Business Metrics')
        db_table = 'business_metrics'
        unique_together = ['business', 'metric_date', 'metric_type']
        indexes = [
            models.Index(fields=['business', 'metric_date', 'metric_type']),
            models.Index(fields=['metric_date']),
        ]
    
    def __str__(self):
        return f"{self.business.name} - {self.metric_date} ({self.metric_type})"


class AuditLog(UUIDMixin, TimestampMixin):
    ACTION_CHOICES = [
        ('CREATE', _('Create')),
        ('UPDATE', _('Update')),
        ('DELETE', _('Delete')),
        ('LOGIN', _('Login')),
        ('LOGOUT', _('Logout')),
        ('EXPORT', _('Export')),
        ('IMPORT', _('Import')),
    ]
    
    business = models.ForeignKey(
        'businesses.Business',
        on_delete=models.CASCADE,
        related_name='audit_logs',
        null=True,
        blank=True
    )
    action = models.CharField(_('action'), max_length=20, choices=ACTION_CHOICES)
    table_name = models.CharField(_('table name'), max_length=100)
    record_id = models.UUIDField(_('record ID'), null=True, blank=True)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    user_email = models.EmailField(_('user email'), blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    old_values = models.JSONField(_('old values'), default=dict, blank=True)
    new_values = models.JSONField(_('new values'), default=dict, blank=True)
    context = models.JSONField(_('context'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business', 'created_at']),
            models.Index(fields=['table_name', 'record_id']),
            models.Index(fields=['user', 'action']),
            models.Index(fields=['action', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.table_name} by {self.user_email or 'System'}"
