from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import UUIDMixin, TimestampMixin, BaseModel
from decimal import Decimal
import uuid


class SubscriptionPlan(UUIDMixin, TimestampMixin):
    name = models.CharField(_('plan name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    price_monthly = models.DecimalField(
        _('monthly price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    price_yearly = models.DecimalField(
        _('yearly price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    currency = models.CharField(_('currency'), max_length=3, default='EUR')
    max_services = models.IntegerField(_('max services'), default=10)
    max_resources = models.IntegerField(_('max resources'), default=5)
    max_appointments_per_month = models.IntegerField(_('max appointments per month'), default=100)
    max_staff_users = models.IntegerField(_('max staff users'), default=3)
    features = models.JSONField(_('features'), default=dict, blank=True)
    stripe_price_id_monthly = models.CharField(_('stripe monthly price ID'), max_length=100, blank=True)
    stripe_price_id_yearly = models.CharField(_('stripe yearly price ID'), max_length=100, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    
    class Meta:
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')
        db_table = 'subscription_plans'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class Subscription(BaseModel):
    BILLING_PERIODS = [
        ('monthly', _('Monthly')),
        ('yearly', _('Yearly')),
    ]
    
    STATUS_CHOICES = [
        ('trialing', _('Trialing')),
        ('active', _('Active')),
        ('past_due', _('Past Due')),
        ('cancelled', _('Cancelled')),
        ('unpaid', _('Unpaid')),
    ]
    
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(_('status'), max_length=50, choices=STATUS_CHOICES, default='trialing')
    billing_period = models.CharField(_('billing period'), max_length=10, choices=BILLING_PERIODS, default='monthly')
    stripe_subscription_id = models.CharField(_('Stripe subscription ID'), max_length=255, unique=True, blank=True)
    stripe_customer_id = models.CharField(_('Stripe customer ID'), max_length=255, blank=True)
    current_period_start = models.DateTimeField(_('current period start'))
    current_period_end = models.DateTimeField(_('current period end'))
    trial_end = models.DateTimeField(_('trial end'), null=True, blank=True)
    cancelled_at = models.DateTimeField(_('cancelled at'), null=True, blank=True)
    usage_data = models.JSONField(_('usage data'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')
        db_table = 'subscriptions'
        indexes = [
            models.Index(fields=['business', 'status']),
            models.Index(fields=['current_period_end']),
        ]
    
    def __str__(self):
        return f"{self.business.name} - {self.plan.name} ({self.status})"


class Payment(UUIDMixin, TimestampMixin):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('succeeded', _('Succeeded')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(
        _('amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(_('currency'), max_length=3)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent_id = models.CharField(_('stripe payment intent ID'), max_length=100, blank=True)
    stripe_charge_id = models.CharField(_('stripe charge ID'), max_length=100, blank=True)
    paid_at = models.DateTimeField(_('paid at'), null=True, blank=True)
    failed_at = models.DateTimeField(_('failed at'), null=True, blank=True)
    failure_reason = models.TextField(_('failure reason'), blank=True)
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscription', 'status']),
            models.Index(fields=['business', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.business.name} - {self.amount} {self.currency} ({self.status})"
