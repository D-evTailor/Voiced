from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.core.utils import PHONE_REGEX_VALIDATOR, LANGUAGE_CHOICES, CURRENCY_CHOICES
import uuid

class Business(UUIDMixin, TimestampMixin):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_businesses',
        verbose_name=_('owner'),
        help_text=_('Business owner and primary contact')
    )
    name = models.CharField(
        _('business name'),
        max_length=200,
        help_text=_('Official business name')
    )
    slug = models.SlugField(
        _('URL slug'),
        max_length=50,
        unique=True,
        help_text=_('Unique URL identifier for public pages')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Brief description of the business')
    )
    email = models.EmailField(
        _('business email'),
        help_text=_('Main business contact email')
    )
    phone = models.CharField(
        _('phone number'),
        validators=[PHONE_REGEX_VALIDATOR],
        max_length=17,
        help_text=_('Business phone number')
    )
    website = models.URLField(
        _('website'),
        blank=True,
        help_text=_('Business website URL')
    )
    address = models.TextField(
        _('address'),
        help_text=_('Complete business address')
    )
    city = models.CharField(
        _('city'),
        max_length=100
    )
    state = models.CharField(
        _('state/province'),
        max_length=100
    )
    postal_code = models.CharField(
        _('postal code'),
        max_length=20
    )
    country = models.CharField(
        _('country'),
        max_length=100,
        default='Spain'
    )
    locale = models.CharField(
        _('business locale'),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='es',
        help_text=_('Primary language for this business')
    )
    timezone = models.CharField(
        _('timezone'),
        max_length=50,
        default='Europe/Madrid',
        help_text=_('Business timezone for appointments')
    )
    currency = models.CharField(
        _('currency'),
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='EUR',
        help_text=_('Currency for pricing')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Whether this business is currently active')
    )
    allow_online_booking = models.BooleanField(
        _('allow online booking'),
        default=True,
        help_text=_('Allow customers to book appointments online')
    )
    allow_voice_booking = models.BooleanField(
        _('allow voice booking'),
        default=True,
        help_text=_('Allow customers to book via voice agent')
    )
    require_approval = models.BooleanField(
        _('require approval'),
        default=False,
        help_text=_('Require manual approval for new appointments')
    )
    logo = models.ImageField(
        _('logo'),
        upload_to='business_logos/',
        blank=True,
        null=True,
        help_text=_('Business logo for branding')
    )
    primary_color = models.CharField(
        _('primary color'),
        max_length=7,
        default='#3B82F6',
        help_text=_('Primary brand color (hex code)')
    )
    
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
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='business_hours',
        verbose_name=_('business')
    )
    day_of_week = models.IntegerField(
        _('day of week'),
        choices=DAYS_OF_WEEK
    )
    open_time = models.TimeField(
        _('opening time'),
        null=True,
        blank=True,
        help_text=_('Leave blank if closed this day')
    )
    close_time = models.TimeField(
        _('closing time'),
        null=True,
        blank=True,
        help_text=_('Leave blank if closed this day')
    )
    is_closed = models.BooleanField(
        _('closed'),
        default=False,
        help_text=_('Mark as closed for this day')
    )
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
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name=_('business')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_memberships',
        verbose_name=_('user')
    )
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='staff'
    )
    permissions = models.JSONField(_('permissions'), default=dict, blank=True)
    is_primary = models.BooleanField(_('primary'), default=False)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Whether this membership is currently active')
    )
    joined_at = models.DateTimeField(_('joined at'), auto_now_add=True)
    class Meta:
        verbose_name = _('Business Member')
        verbose_name_plural = _('Business Members')
        db_table = 'business_members'
        unique_together = ['business', 'user']
        ordering = ['business', 'role', 'user']
    def __str__(self):
        return f"{self.user.email} - {self.business.name} ({self.role})"
