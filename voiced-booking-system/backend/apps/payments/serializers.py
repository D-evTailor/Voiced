from rest_framework import serializers
from .models import Subscription, SubscriptionPlan, Payment


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'description', 'price_monthly', 'price_yearly',
            'currency', 'max_services', 'max_resources', 
            'max_appointments_per_month', 'max_staff_users', 'features'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'status', 'billing_period', 'current_period_start',
            'current_period_end', 'trial_end', 'cancelled_at', 'usage_data'
        ]
        read_only_fields = [
            'stripe_subscription_id', 'stripe_customer_id', 'usage_data'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'currency', 'status', 'paid_at', 
            'failed_at', 'failure_reason', 'created_at'
        ]
        read_only_fields = [
            'stripe_payment_intent_id', 'stripe_charge_id'
        ]
