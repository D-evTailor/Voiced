from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import UUIDMixin, TimestampMixin, BaseModel


class NotificationTemplate(UUIDMixin, TimestampMixin):
    TEMPLATE_TYPES = [
        ('appointment_confirmed', _('Appointment Confirmed')),
        ('appointment_reminder', _('Appointment Reminder')),
        ('appointment_cancelled', _('Appointment Cancelled')),
        ('payment_successful', _('Payment Successful')),
        ('payment_failed', _('Payment Failed')),
        ('subscription_expiring', _('Subscription Expiring')),
        ('welcome', _('Welcome')),
        ('password_reset', _('Password Reset')),
    ]
    
    CHANNEL_TYPES = [
        ('email', _('Email')),
        ('sms', _('SMS')),
        ('push', _('Push Notification')),
        ('webhook', _('Webhook')),
    ]
    
    business = models.ForeignKey(
        'businesses.Business',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notification_templates'
    )
    name = models.CharField(_('template name'), max_length=100)
    type = models.CharField(_('type'), max_length=50, choices=TEMPLATE_TYPES)
    channel = models.CharField(_('channel'), max_length=20, choices=CHANNEL_TYPES)
    subject_template = models.TextField(_('subject template'), blank=True)
    body_template = models.TextField(_('body template'))
    is_active = models.BooleanField(_('active'), default=True)
    is_system_default = models.BooleanField(_('system default'), default=False)
    
    class Meta:
        verbose_name = _('Notification Template')
        verbose_name_plural = _('Notification Templates')
        db_table = 'notification_templates'
        unique_together = ['business', 'type', 'channel']
        indexes = [
            models.Index(fields=['business', 'type', 'is_active']),
            models.Index(fields=['is_system_default']),
        ]
    
    def __str__(self):
        business_name = self.business.name if self.business else "System"
        return f"{business_name} - {self.name} ({self.channel})"


class Notification(UUIDMixin, TimestampMixin):
    RECIPIENT_TYPES = [
        ('user', _('User')),
        ('client', _('Client')),
        ('staff', _('Staff')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]
    
    business = models.ForeignKey(
        'businesses.Business',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    recipient_type = models.CharField(_('recipient type'), max_length=20, choices=RECIPIENT_TYPES)
    recipient_id = models.UUIDField(_('recipient ID'), null=True, blank=True)
    recipient_email = models.EmailField(_('recipient email'), blank=True)
    recipient_phone = models.CharField(_('recipient phone'), max_length=20, blank=True)
    channel = models.CharField(_('channel'), max_length=20, choices=NotificationTemplate.CHANNEL_TYPES)
    subject = models.TextField(_('subject'), blank=True)
    body = models.TextField(_('body'))
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(_('sent at'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('delivered at'), null=True, blank=True)
    failed_at = models.DateTimeField(_('failed at'), null=True, blank=True)
    failure_reason = models.TextField(_('failure reason'), blank=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business', 'status', 'created_at']),
            models.Index(fields=['recipient_type', 'recipient_id']),
            models.Index(fields=['channel', 'status']),
        ]
    
    def __str__(self):
        return f"{self.recipient_email or self.recipient_phone} - {self.subject[:50]} ({self.status})"
