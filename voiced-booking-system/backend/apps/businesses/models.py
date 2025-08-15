from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import BusinessModel, TimestampMixin, CountMixin
from apps.core.utils import PHONE_REGEX_VALIDATOR
from apps.core.choices import CURRENCY_CHOICES, BUSINESS_TYPE_CHOICES, LANGUAGE_CHOICES


class Business(BusinessModel, CountMixin):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_businesses',
        verbose_name=_('owner')
    )
    name = models.CharField(_('business name'), max_length=200)
    slug = models.SlugField(_('URL slug'), max_length=50, unique=True)
    description = models.TextField(_('description'), blank=True)
    email = models.EmailField(_('business email'))
    phone = models.CharField(_('phone number'), validators=[PHONE_REGEX_VALIDATOR], max_length=17)
    website = models.URLField(_('website'), blank=True)
    address = models.TextField(_('address'))
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state/province'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20)
    country = models.CharField(_('country'), max_length=100, default='Spain')
    business_type = models.CharField(_('business type'), max_length=50, choices=BUSINESS_TYPE_CHOICES, default='other')
    locale = models.CharField(_('business locale'), max_length=10, choices=LANGUAGE_CHOICES, default='es')
    timezone = models.CharField(_('timezone'), max_length=50, default='Europe/Madrid')
    currency = models.CharField(_('currency'), max_length=3, choices=CURRENCY_CHOICES, default='EUR')
    allow_online_booking = models.BooleanField(_('allow online booking'), default=True)
    allow_voice_booking = models.BooleanField(_('allow voice booking'), default=True)
    require_approval = models.BooleanField(_('require approval'), default=False)
    logo = models.ImageField(_('logo'), upload_to='business_logos/', blank=True, null=True)
    primary_color = models.CharField(_('primary color'), max_length=7, default='#3B82F6')
    subscription_status = models.CharField(
        _('subscription status'),
        max_length=20,
        choices=[
            ('trial', _('Trial')),
            ('active', _('Active')),
            ('suspended', _('Suspended')),
            ('cancelled', _('Cancelled')),
        ],
        default='trial'
    )
    trial_ends_at = models.DateTimeField(_('trial ends at'), null=True, blank=True)
    _count_relation = 'members'
    
    class Meta:
        verbose_name = _('Business')
        verbose_name_plural = _('Businesses')
        db_table = 'businesses'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['owner']),
            models.Index(fields=['is_active']),
            models.Index(fields=['locale']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.postal_code}, {self.country}"

class BusinessHours(models.Model):
    DAYS_OF_WEEK = [
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_hours')
    day_of_week = models.IntegerField(_('day of week'), choices=DAYS_OF_WEEK)
    open_time = models.TimeField(_('opening time'), null=True, blank=True)
    close_time = models.TimeField(_('closing time'), null=True, blank=True)
    is_closed = models.BooleanField(_('closed'), default=False)
    
    class Meta:
        verbose_name = _('Business Hours')
        verbose_name_plural = _('Business Hours')
        db_table = 'business_hours'
        unique_together = ['business', 'day_of_week']
        ordering = ['business', 'day_of_week']
    
    def __str__(self):
        day_name = self.get_day_of_week_display()
        if self.is_closed or not self.open_time or not self.close_time:
            return f"{self.business.name} - {day_name}: Closed"
        return f"{self.business.name} - {day_name}: {self.open_time} - {self.close_time}"
    
    @property
    def is_open(self):
        return not self.is_closed and self.open_time and self.close_time


class BusinessMember(TimestampMixin):
    ROLE_CHOICES = [
        ('owner', _('Owner')),
        ('admin', _('Administrator')),
        ('manager', _('Manager')),
        ('staff', _('Staff')),
        ('viewer', _('Viewer')),
    ]
    
    ROLE_PERMISSIONS = {
        'owner': ['all'],
        'admin': ['manage_users', 'manage_services', 'view_reports', 'manage_appointments', 'manage_settings'],
        'manager': ['manage_services', 'view_reports', 'manage_appointments'],
        'staff': ['view_appointments', 'create_appointments'],
        'viewer': ['view_appointments'],
    }
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_memberships')
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default='staff')
    is_primary = models.BooleanField(_('primary'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    joined_at = models.DateTimeField(_('joined at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Business Member')
        verbose_name_plural = _('Business Members')
        db_table = 'business_members'
        unique_together = ['business', 'user']
        ordering = ['business', 'role', 'user']
    
    def __str__(self):
        return f"{self.user.email} - {self.business.name} ({self.role})"
    
    def has_permission(self, permission):
        if self.role == 'owner':
            return True
        return permission in self.ROLE_PERMISSIONS.get(self.role, [])
