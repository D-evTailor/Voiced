from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class VersionMixin(models.Model):
    version = models.PositiveIntegerField(default=1)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if self.pk:
            self.version += 1
        super().save(*args, **kwargs)


class OrderMixin(models.Model):
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        abstract = True


class ActiveMixin(models.Model):
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        abstract = True


class AuditMixin(TimestampMixin, VersionMixin):
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
        self.save()
    
    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.save()
    
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


class BaseModel(UUIDMixin, AuditMixin, SoftDeleteMixin, TenantMixin, ActiveMixin):
    class Meta:
        abstract = True


class SimpleModel(UUIDMixin, TimestampMixin, ActiveMixin):
    class Meta:
        abstract = True


class BusinessModel(UUIDMixin, TimestampMixin, VersionMixin, ActiveMixin):
    class Meta:
        abstract = True


class CountMixin(models.Model):
    class Meta:
        abstract = True
    
    @property
    def active_count(self):
        return getattr(self, self._count_relation).filter(is_active=True).count()


class TimeCalculationMixin(models.Model):
    class Meta:
        abstract = True
    
    @property
    def end_time(self):
        if hasattr(self, 'start_time') and hasattr(self, 'service') and self.start_time and self.service:
            from datetime import timedelta
            return self.start_time + timedelta(minutes=self.service.duration)
        return None
    
    @property
    def duration_display(self):
        if hasattr(self, 'duration'):
            hours, minutes = divmod(self.duration, 60)
            if hours:
                return f"{hours}h {minutes}m" if minutes else f"{hours}h"
            return f"{minutes}m"
        return None
    
    @property
    def total_time_required(self):
        if hasattr(self, 'duration') and hasattr(self, 'buffer_time'):
            return self.duration + self.buffer_time
        return getattr(self, 'duration', 0)
