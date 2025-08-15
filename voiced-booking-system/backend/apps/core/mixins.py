from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from .helpers import format_duration, calculate_end_time, safe_decimal_add


class BaseFieldsMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        abstract = True


class AuditFieldsMixin(models.Model):
    version = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if self.pk:
            self.version += 1
        super().save(*args, **kwargs)


class SoftDeleteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)
    
    def deleted(self):
        return self.filter(deleted_at__isnull=False)
    
    def delete(self):
        return self.update(deleted_at=timezone.now())
    
    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).active()
    
    def with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)
    
    def deleted_only(self):
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()


class SoftDeleteMixin(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted'
    )
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
    
    def delete(self, user=None):
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=['deleted_at', 'deleted_by'])
    
    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['deleted_at', 'deleted_by'])
    
    def hard_delete(self):
        super().delete()
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None


class TenantQuerySet(models.QuerySet):
    def for_business(self, business):
        return self.filter(business=business)


class TenantManager(models.Manager):
    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db)
    
    def for_business(self, business):
        return self.get_queryset().for_business(business)


class TenantMixin(models.Model):
    business = models.ForeignKey(
        'businesses.Business',
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )
    
    objects = TenantManager()
    
    class Meta:
        abstract = True


class OrderMixin(models.Model):
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        abstract = True
        ordering = ['order']


class BaseModel(BaseFieldsMixin, AuditFieldsMixin, SoftDeleteMixin, TenantMixin):
    class Meta:
        abstract = True


class SimpleModel(BaseFieldsMixin):
    class Meta:
        abstract = True


class BusinessModel(BaseFieldsMixin, AuditFieldsMixin):
    class Meta:
        abstract = True


class BusinessStatsMixin(models.Model):
    class Meta:
        abstract = True
    
    def update_client_stats(self):
        if hasattr(self, 'client') and self.client:
            appointments = self.client.appointments.filter(status__in=['completed', 'confirmed'])
            self.client.total_appointments = appointments.count()
            self.client.total_spent = safe_decimal_add(
                *[apt.final_price for apt in appointments if apt.final_price]
            )
            last_apt = appointments.order_by('-start_time').first()
            self.client.last_appointment_date = last_apt.start_time if last_apt else None
            self.client.save(update_fields=['total_appointments', 'total_spent', 'last_appointment_date'])


class TimeCalculationMixin(models.Model):
    class Meta:
        abstract = True
    
    @property
    def end_time(self):
        if hasattr(self, 'start_time') and hasattr(self, 'service'):
            return calculate_end_time(self.start_time, getattr(self.service, 'duration', None))
        return None
    
    @property
    def duration_display(self):
        duration = getattr(self, 'duration', None)
        return format_duration(duration)
