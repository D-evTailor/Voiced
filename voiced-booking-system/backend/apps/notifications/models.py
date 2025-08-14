from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import TimestampMixin

class NotificationTemplate(TimestampMixin):
    TYPE_CHOICES = [
        ('email', _('Email')),
        ('sms', _('SMS')),
    ]
    
    name = models.CharField(_('template name'), max_length=100)
    type = models.CharField(_('type'), max_length=10, choices=TYPE_CHOICES)
    subject = models.CharField(_('subject'), max_length=200, blank=True)
    content = models.TextField(_('content'))
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('Notification Template')
        verbose_name_plural = _('Notification Templates')
        db_table = 'notification_templates'
    
    def __str__(self):
        return f"{self.name} ({self.type})"
