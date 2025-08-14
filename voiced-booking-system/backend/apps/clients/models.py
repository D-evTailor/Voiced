from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import BaseModel
from apps.core.managers import TenantManager
from apps.core.utils import PHONE_REGEX_VALIDATOR, LANGUAGE_CHOICES
from decimal import Decimal


class Client(BaseModel):
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone number'), validators=[PHONE_REGEX_VALIDATOR], max_length=17, blank=True)
    
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    preferred_language = models.CharField(
        _('preferred language'),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='es'
    )
    
    notes = models.TextField(_('notes'), blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    objects = TenantManager()
    
    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        db_table = 'clients'
        
        constraints = [
            models.CheckConstraint(
                check=models.Q(email__isnull=False) | models.Q(phone__isnull=False),
                name='client_must_have_email_or_phone'
            ),
        ]
        
        indexes = [
            models.Index(fields=['business', 'email'], name='idx_client_business_email'),
            models.Index(fields=['business', 'phone'], name='idx_client_business_phone'),
            models.Index(fields=['business', 'first_name', 'last_name'], name='idx_client_business_name'),
            models.Index(fields=['business', 'is_active'], name='idx_client_business_active'),
        ]
        
        unique_together = [
            ('business', 'email'),
            ('business', 'phone'),
        ]
        
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.business.name}"
    
    def get_full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email or self.phone or f"Client #{self.id[:8]}"
    
    def get_display_name(self):
        full_name = self.get_full_name()
        if full_name != self.email and full_name != self.phone:
            return full_name
        return f"{full_name[:20]}..." if len(full_name) > 20 else full_name
