from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import uuid
from .helpers import format_duration, calculate_end_time, safe_decimal_add
from .exceptions import success_response, error_response


class IdempotencyMixin:
    def get_idempotency_key(self, request):
        return request.headers.get('Idempotency-Key')
    
    def check_idempotency(self, request):
        key = self.get_idempotency_key(request)
        if not key:
            return None
        
        from django.core.cache import cache
        cached_response = cache.get(f'idempotency:{key}')
        if cached_response:
            return Response(cached_response['data'], status=cached_response['status'])
        return None
    
    def store_idempotent_response(self, request, response):
        key = self.get_idempotency_key(request)
        if key and hasattr(response, 'data'):
            from django.core.cache import cache
            cache.set(f'idempotency:{key}', {
                'data': response.data,
                'status': response.status_code
            }, timeout=3600)
    
    def create(self, request, *args, **kwargs):
        cached_response = self.check_idempotency(request)
        if cached_response:
            return cached_response
        
        response = super().create(request, *args, **kwargs)
        self.store_idempotent_response(request, response)
        return response


class ResourceActionsMixin:
    @action(detail=False, methods=['get'])
    def count(self, request):
        count = self.get_queryset().count()
        return success_response(data={'count': count})
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return error_response('No IDs provided')
        
        queryset = self.get_queryset().filter(id__in=ids)
        count = queryset.count()
        queryset.delete()
        
        return success_response(
            data={'deleted_count': count},
            message=f'{count} items deleted'
        )
    
    @action(detail=False, methods=['patch'])
    def bulk_update(self, request):
        updates = request.data.get('updates', [])
        if not updates:
            return error_response('No updates provided')
        
        updated_count = 0
        for update in updates:
            item_id = update.get('id')
            if not item_id:
                continue
            
            try:
                instance = self.get_queryset().get(id=item_id)
                serializer = self.get_serializer(instance, data=update, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated_count += 1
            except self.queryset.model.DoesNotExist:
                continue
        
        return success_response(
            data={'updated_count': updated_count},
            message=f'{updated_count} items updated'
        )


class CacheOptimizationMixin:
    cache_timeout = 300
    
    def get_cache_key(self, request):
        business_id = getattr(request, 'business', None) and request.business.id
        user_id = request.user.id
        query_params = sorted(request.query_params.items())
        return f"{self.__class__.__name__}:{business_id}:{user_id}:{hash(tuple(query_params))}"
    
    def get_cached_response(self, request):
        if request.method != 'GET':
            return None
        
        from django.core.cache import cache
        cache_key = self.get_cache_key(request)
        return cache.get(cache_key)
    
    def cache_response(self, request, response):
        if request.method == 'GET' and hasattr(response, 'data'):
            from django.core.cache import cache
            cache_key = self.get_cache_key(request)
            cache.set(cache_key, response.data, timeout=self.cache_timeout)
    
    def list(self, request, *args, **kwargs):
        cached_response = self.get_cached_response(request)
        if cached_response:
            return Response(cached_response)
        
        response = super().list(request, *args, **kwargs)
        self.cache_response(request, response)
        return response


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


class TenantMixin(models.Model):
    from .managers import TenantManager
    
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
