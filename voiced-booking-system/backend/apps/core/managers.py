from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


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
