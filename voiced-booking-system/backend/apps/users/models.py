from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import BaseFieldsMixin, SimpleModel
from apps.core.choices import LANGUAGE_CHOICES


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True, validators=[EmailValidator()])
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_verified = models.BooleanField(_('verified'), default=False)
    locale = models.CharField(_('locale'), max_length=10, choices=LANGUAGE_CHOICES, default='es')
    timezone = models.CharField(_('timezone'), max_length=50, default='Europe/Madrid')
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'is_verified']),
            models.Index(fields=['locale']),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email

    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]

    @property
    def display_name(self):
        return self.get_full_name()


class UserProfile(BaseFieldsMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True, null=True)
    email_notifications = models.BooleanField(_('email notifications'), default=True)
    sms_notifications = models.BooleanField(_('SMS notifications'), default=False)
    marketing_emails = models.BooleanField(_('marketing emails'), default=False)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        db_table = 'user_profiles'

    def __str__(self):
        return f'{self.user.email} Profile'


class UserSession(SimpleModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    token_jti = models.CharField(_('JWT ID'), max_length=255, unique=True, db_index=True)
    device_info = models.JSONField(_('device information'), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'))
    user_agent = models.TextField(_('user agent'), blank=True)
    expires_at = models.DateTimeField(_('expires at'))
    revoked_at = models.DateTimeField(_('revoked at'), null=True, blank=True)
    last_activity = models.DateTimeField(_('last activity'), auto_now=True)
    
    class Meta:
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        db_table = 'user_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'expires_at']),
            models.Index(fields=['token_jti']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.created_at}"
    
    @property
    def is_expired(self):
        return self.expires_at < timezone.now()
    
    @property
    def is_active(self):
        return not self.is_expired and not self.revoked_at
    
    def revoke(self):
        self.revoked_at = timezone.now()
        self.save()


class LoginAttempt(SimpleModel):
    FAILURE_REASONS = [
        ('invalid_credentials', _('Invalid credentials')),
        ('account_disabled', _('Account disabled')),
        ('account_locked', _('Account locked')),
        ('rate_limited', _('Rate limited')),
        ('invalid_2fa', _('Invalid 2FA code')),
        ('other', _('Other')),
    ]
    
    email = models.EmailField(_('email attempted'), db_index=True)
    ip_address = models.GenericIPAddressField(_('IP address'), db_index=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    success = models.BooleanField(_('successful'))
    failure_reason = models.CharField(_('failure reason'), max_length=100, blank=True, choices=FAILURE_REASONS)
    user_found = models.BooleanField(_('user found'), default=False)
    country = models.CharField(_('country'), max_length=100, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Login Attempt')
        verbose_name_plural = _('Login Attempts')
        db_table = 'login_attempts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['success', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.email} from {self.ip_address}"
    
    @classmethod
    def get_recent_failures_for_email(cls, email, minutes=15):
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(
            email=email,
            success=False,
            created_at__gte=cutoff
        ).count()
    
    @classmethod
    def get_recent_failures_for_ip(cls, ip_address, minutes=15):
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(
            ip_address=ip_address,
            success=False,
            created_at__gte=cutoff
        ).count()
