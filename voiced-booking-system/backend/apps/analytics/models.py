from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import TimestampMixin

class BusinessMetrics(TimestampMixin):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField(_('date'))
    total_appointments = models.PositiveIntegerField(_('total appointments'), default=0)
    completed_appointments = models.PositiveIntegerField(_('completed appointments'), default=0)
    cancelled_appointments = models.PositiveIntegerField(_('cancelled appointments'), default=0)
    revenue = models.DecimalField(_('revenue'), max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('Business Metrics')
        verbose_name_plural = _('Business Metrics')
        db_table = 'business_metrics'
        unique_together = ['business', 'date']
    
    def __str__(self):
        return f"{self.business.name} - {self.date}"
