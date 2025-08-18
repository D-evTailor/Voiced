from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from apps.core.viewsets import TenantViewSet
from .models import Subscription
from .serializers import SubscriptionSerializer
import json
import logging

logger = logging.getLogger(__name__)


class SubscriptionViewSet(TenantViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        return super().get_queryset().filter(business=self.request.tenant)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        try:
            subscription.status = 'cancelled'
            subscription.save()
            return Response({'status': 'cancelled'})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        logger.info(f"Stripe webhook received")
        return HttpResponse(status=200)


class PaymentViewSet(TenantViewSet):
    queryset = None
    serializer_class = None
