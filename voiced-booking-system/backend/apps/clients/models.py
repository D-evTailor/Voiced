from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import BaseModel
from apps.core.managers import TenantManager
from apps.core.utils import PHONE_REGEX_VALIDATOR, LANGUAGE_CHOICES
from decimal import Decimal


class Client(BaseModel):
    GENDER_CHOICES = [
        ('male', _('Male')),
        ('female', _('Female')),
        ('other', _('Other')),
        ('prefer_not_to_say', _('Prefer not to say')),
    ]
    
    SOURCE_CHOICES = [
        ('website', _('Website')),
        ('social_media', _('Social Media')),
        ('referral', _('Referral')),
        ('voice_agent', _('Voice Agent')),
        ('walk_in', _('Walk In')),
        ('google', _('Google Search')),
        ('other', _('Other')),
    ]
    
    SEGMENT_CHOICES = [
        ('new', _('New Client')),
        ('regular', _('Regular Client')),
        ('vip', _('VIP Client')),
        ('at_risk', _('At Risk')),
        ('inactive', _('Inactive')),
    ]

    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100, blank=True)
    email = models.EmailField(_('email'), blank=True)
    
    phone = models.CharField(_('phone number'), validators=[PHONE_REGEX_VALIDATOR], max_length=17, blank=True)
    
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    gender = models.CharField(_('gender'), max_length=20, choices=GENDER_CHOICES, blank=True)
    
    address_line1 = models.CharField(_('address line 1'), max_length=200, blank=True)
    address_line2 = models.CharField(_('address line 2'), max_length=200, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    country = models.CharField(_('country'), max_length=100, default='Spain')
    
    preferred_language = models.CharField(
        _('preferred language'),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='es'
    )
    communication_preferences = models.JSONField(
        _('communication preferences'),
        default=lambda: {'email': True, 'sms': False, 'phone_calls': True, 'marketing_emails': False}
    )
    
    allergies = models.TextField(_('allergies'), blank=True)
    medical_conditions = models.TextField(_('medical conditions'), blank=True)
    emergency_contact = models.JSONField(_('emergency contact'), default=dict, blank=True)
    
    total_appointments = models.PositiveIntegerField(_('total appointments'), default=0)
    completed_appointments = models.PositiveIntegerField(_('completed appointments'), default=0)
    cancelled_appointments = models.PositiveIntegerField(_('cancelled appointments'), default=0)
    no_show_appointments = models.PositiveIntegerField(_('no show appointments'), default=0)
    
    total_spent = models.DecimalField(
        _('total spent'), max_digits=10, decimal_places=2, default=Decimal('0.00')
    )
    average_spending = models.DecimalField(
        _('average spending'), max_digits=10, decimal_places=2, default=Decimal('0.00')
    )
    
    first_appointment_date = models.DateTimeField(_('first appointment'), null=True, blank=True)
    last_appointment_date = models.DateTimeField(_('last appointment'), null=True, blank=True)
    
    source = models.CharField(_('acquisition source'), max_length=50, blank=True, choices=SOURCE_CHOICES)
    referral_source = models.CharField(_('referral source'), max_length=100, blank=True)
    marketing_consent = models.BooleanField(_('marketing consent'), default=False)
    
    client_segment = models.CharField(
        _('client segment'), max_length=20, choices=SEGMENT_CHOICES, default='new'
    )
    loyalty_points = models.PositiveIntegerField(_('loyalty points'), default=0)
    
    notes = models.TextField(_('public notes'), blank=True)
    internal_notes = models.TextField(_('internal notes'), blank=True)
    
    is_active = models.BooleanField(_('active'), default=True)
    is_blacklisted = models.BooleanField(_('blacklisted'), default=False)
    blacklist_reason = models.TextField(_('blacklist reason'), blank=True)
    
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
            models.CheckConstraint(
                check=models.Q(total_spent__gte=0),
                name='client_total_spent_non_negative'
            ),
        ]
        
        indexes = [
            models.Index(fields=['business', 'email'], name='idx_client_business_email'),
            models.Index(fields=['business', 'phone'], name='idx_client_business_phone'),
            models.Index(fields=['business', 'first_name', 'last_name'], name='idx_client_business_name'),
            models.Index(fields=['business', 'is_active'], name='idx_client_business_active'),
            models.Index(fields=['business', 'client_segment'], name='idx_client_business_segment'),
            models.Index(fields=['last_appointment_date'], name='idx_client_last_appointment'),
            models.Index(fields=['total_spent'], name='idx_client_total_spent'),
        ]
        
        unique_together = [
            ('business', 'email'),
            ('business', 'phone'),
        ]
        
        ordering = ['-last_appointment_date', '-created_at']
    
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
    
    @property
    def completion_rate(self):
        if self.total_appointments == 0:
            return 0
        return (self.completed_appointments / self.total_appointments) * 100
    
    @property
    def lifetime_value(self):
        return self.total_spent
    
    def update_statistics(self):
        from apps.appointments.models import Appointment
        
        appointments = Appointment.objects.filter(client=self)
        
        self.total_appointments = appointments.count()
        self.completed_appointments = appointments.filter(status='completed').count()
        self.cancelled_appointments = appointments.filter(status='cancelled').count()
        self.no_show_appointments = appointments.filter(status='no_show').count()
        
        completed = appointments.filter(status='completed', final_price__isnull=False)
        self.total_spent = completed.aggregate(
            total=models.Sum('final_price')
        )['total'] or Decimal('0.00')
        
        if self.completed_appointments > 0:
            self.average_spending = self.total_spent / self.completed_appointments
        
        first_apt = appointments.order_by('start_time').first()
        last_apt = appointments.order_by('-start_time').first()
        
        if first_apt:
            self.first_appointment_date = first_apt.start_time
        if last_apt:
            self.last_appointment_date = last_apt.start_time
        
        self.update_client_segment()
        self.save()
    
    def update_client_segment(self):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        ninety_days_ago = now - timedelta(days=90)
        
        if self.total_spent >= 500 or self.completed_appointments >= 10:
            self.client_segment = 'vip'
        elif (self.last_appointment_date and 
              self.last_appointment_date >= thirty_days_ago and 
              self.completed_appointments >= 3):
            self.client_segment = 'regular'
        elif (self.last_appointment_date and 
              self.last_appointment_date < thirty_days_ago and 
              self.last_appointment_date >= ninety_days_ago and
              self.completed_appointments >= 2):
            self.client_segment = 'at_risk'
        elif (not self.last_appointment_date or 
              self.last_appointment_date < ninety_days_ago):
            self.client_segment = 'inactive'
        else:
            self.client_segment = 'new'
