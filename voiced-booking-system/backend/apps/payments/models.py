from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import BaseModel
import uuid

class Subscription(BaseModel):
    stripe_subscription_id = models.CharField(_('Stripe subscription ID'), max_length=255, unique=True)
    status = models.CharField(_('status'), max_length=50)
    
    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')
        db_table = 'subscriptions'
    
    def __str__(self):
        return f"{self.business.name} - {self.status}"
