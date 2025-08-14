from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.apps import apps


class TenantQuerySet(models.QuerySet):
    def for_business(self, business):
        return self.filter(business=business)
    
    def active(self):
        return self.filter(deleted_at__isnull=True)


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
            self.validate_subscription_limits(business)
        return super().create(**kwargs)
    
    def validate_subscription_limits(self, business):
        subscription = getattr(business, 'subscription', None)
        if not subscription or subscription.status != 'active':
            return True
            
        model_name = self.model.__name__
        limit_mappings = {
            'Service': 'max_services',
            'Resource': 'max_resources', 
            'BusinessMember': 'max_staff_users',
        }
        
        limit_field = limit_mappings.get(model_name)
        if not limit_field:
            return True
            
        limit = getattr(subscription.plan, limit_field, None)
        if not limit or limit == -1:
            return True
            
        current_count = self.for_business(business).active().count()
        
        if current_count >= limit:
            raise ValidationError(
                _('You have reached the limit of {limit} {model_name} for your {plan_name} plan. '
                  'Please upgrade to continue.').format(
                    limit=limit,
                    model_name=self.model._meta.verbose_name_plural,
                    plan_name=subscription.plan.name
                )
            )
        
        return True


def validate_business_limits(business, model_class, limit_field):
    if not hasattr(business, 'subscription') or not business.subscription:
        return
    
    subscription = business.subscription
    plan = subscription.plan
    
    current_count = model_class.objects.for_business(business).active().count()
    limit = getattr(plan, limit_field, None)
    
    if limit and limit > 0 and current_count >= limit:
        raise ValidationError(
            _('You have reached the limit of {limit} {model_name} for your current plan.').format(
                limit=limit,
                model_name=model_class._meta.verbose_name_plural
            )
        )
