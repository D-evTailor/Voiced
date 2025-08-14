from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import TimestampMixin

class VapiConfig(TimestampMixin):
    business = models.OneToOneField('businesses.Business', on_delete=models.CASCADE, related_name='vapi_config')
    assistant_id = models.CharField(_('Vapi assistant ID'), max_length=255)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('Vapi Configuration')
        verbose_name_plural = _('Vapi Configurations')
        db_table = 'vapi_configs'
    
    def __str__(self):
        return f"{self.business.name} - Vapi Config"
