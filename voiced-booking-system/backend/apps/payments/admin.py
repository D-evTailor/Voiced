from django.contrib import admin
from .models import SubscriptionPlan, Subscription, Payment


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_monthly', 'price_yearly', 'max_services', 'is_active']
    list_filter = ['is_active', 'currency']
    ordering = ['sort_order', 'name']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['business', 'plan', 'status', 'billing_period', 'current_period_end']
    list_filter = ['status', 'billing_period', 'plan']
    search_fields = ['business__name']
    ordering = ['-created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['business', 'amount', 'currency', 'status', 'paid_at']
    list_filter = ['status', 'currency']
    search_fields = ['business__name', 'stripe_payment_intent_id']
    ordering = ['-created_at']
