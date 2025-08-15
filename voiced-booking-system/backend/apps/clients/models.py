from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import BaseModel
from apps.core.managers import TenantManager
from apps.core.utils import PHONE_REGEX_VALIDATOR
from apps.core.choices import LANGUAGE_CHOICES
from apps.core.helpers import get_display_name, normalize_phone_number


class Client(BaseModel):
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone number'), validators=[PHONE_REGEX_VALIDATOR], max_length=17, blank=True)
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    preferred_language = models.CharField(_('preferred language'), max_length=10, choices=LANGUAGE_CHOICES, default='es')
    notes = models.TextField(_('notes'), blank=True)
    
    total_spent = models.DecimalField(_('total spent'), max_digits=10, decimal_places=2, default=0)
    total_appointments = models.PositiveIntegerField(_('total appointments'), default=0)
    last_appointment_date = models.DateTimeField(_('last appointment'), null=True, blank=True)
    preferred_staff = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='preferred_clients')
    marketing_consent = models.BooleanField(_('marketing consent'), default=False)
    voice_recognition_id = models.CharField(_('voice ID'), max_length=255, blank=True)
    
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
        return f"{self.get_display_name()} - {self.business.name}"
    
    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = normalize_phone_number(self.phone)
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        return get_display_name(self, ['first_name', 'last_name'])
    
    def get_display_name(self):
        return get_display_name(self, ['first_name', 'last_name', 'email', 'phone'])
