from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class TenantQuerySet(models.QuerySet):
    def for_business(self, business):
        return self.filter(business=business)
    
    def active(self):
        return self.filter(deleted_at__isnull=True, is_active=True)


class TenantManager(models.Manager):
    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db)
    
    def for_business(self, business):
        return self.get_queryset().for_business(business)
    
    def active(self):
        return self.get_queryset().active()
    
    def create(self, **kwargs):
        business = kwargs.get('business')
        if business:
            self._validate_subscription_limits(business)
        return super().create(**kwargs)
    
    def _validate_subscription_limits(self, business):
        subscription = getattr(business, 'subscription', None)
        if not subscription or subscription.status != 'active':
            return
            
        limit_mappings = {
            'Service': 'max_services',
            'Resource': 'max_resources', 
            'BusinessMember': 'max_staff_users',
        }
        
        limit_field = limit_mappings.get(self.model.__name__)
        if not limit_field:
            return
            
        limit = getattr(subscription.plan, limit_field, -1)
        if limit == -1:
            return
            
        current_count = self.for_business(business).active().count()
        
        if current_count >= limit:
            raise ValidationError(
                _('You have reached the limit of {limit} {model} for your plan.').format(
                    limit=limit,
                    model=self.model._meta.verbose_name_plural
                )
            )
