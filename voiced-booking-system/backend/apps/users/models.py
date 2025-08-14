from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import TimestampMixin


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
    email = models.EmailField(
        _('email address'),
        unique=True,
        validators=[EmailValidator()],
        help_text=_('Required. Enter a valid email address.')
    )
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=True
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active.')
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_('Designates whether the user has verified their email address.')
    )
    locale = models.CharField(
        _('locale'),
        max_length=10,
        choices=[
            ('es', _('Spanish')),
            ('en', _('English')),
        ],
        default='es',
        help_text=_('User preferred language for interface and notifications.')
    )
    timezone = models.CharField(
        _('timezone'),
        max_length=50,
        default='Europe/Madrid',
        help_text=_('User timezone for appointment scheduling.')
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now
    )
    last_login = models.DateTimeField(
        _('last login'),
        blank=True,
        null=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )
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


class UserProfile(TimestampMixin):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('user')
    )
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        help_text=_('Phone number for SMS notifications.')
    )
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text=_('Profile picture.')
    )
    email_notifications = models.BooleanField(
        _('email notifications'),
        default=True,
        help_text=_('Receive notifications via email.')
    )
    sms_notifications = models.BooleanField(
        _('SMS notifications'),
        default=False,
        help_text=_('Receive notifications via SMS.')
    )
    marketing_emails = models.BooleanField(
        _('marketing emails'),
        default=False,
        help_text=_('Receive marketing and promotional emails.')
    )

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        db_table = 'user_profiles'

    def __str__(self):
        return f'{self.user.email} Profile'
