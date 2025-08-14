from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from apps.core.permissions import IsBusinessMember
from apps.businesses.models import Business
from .models import VapiConfiguration, VapiCall
from .serializers import VapiConfigurationSerializer, VapiCallSerializer, VapiWebhookSerializer
from .security import WebhookSecurityManager
from .processors import WebhookProcessor
import logging

logger = logging.getLogger(__name__)


class VapiConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = VapiConfigurationSerializer
    permission_classes = [IsAuthenticated, IsBusinessMember]
    
    def get_queryset(self):
        business_id = self.kwargs.get('business_id') or self.request.query_params.get('business_id')
        if business_id:
            business = get_object_or_404(Business, id=business_id)
            return VapiConfiguration.objects.filter(business=business, is_active=True)
        return VapiConfiguration.objects.none()
    
    def perform_create(self, serializer):
        business_id = self.kwargs.get('business_id') or self.request.data.get('business_id')
        business = get_object_or_404(Business, id=business_id)
        serializer.save(business=business)


class VapiCallViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VapiCallSerializer
    permission_classes = [IsAuthenticated, IsBusinessMember]
    
    def get_queryset(self):
        business_id = self.kwargs.get('business_id') or self.request.query_params.get('business_id')
        if business_id:
            business = get_object_or_404(Business, id=business_id)
            return VapiCall.objects.filter(business=business).select_related(
                'transcript', 'analysis', 'appointment_integration__appointment'
            )
        return VapiCall.objects.none()
    
    @action(detail=True, methods=['get'])
    def transcript(self, request, pk=None):
        call = self.get_object()
        if hasattr(call, 'transcript'):
            return Response({
                'transcript': call.transcript.transcript,
                'messages': call.transcript.messages
            })
        return Response({'transcript': '', 'messages': []})
    
    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        call = self.get_object()
        if hasattr(call, 'analysis'):
            return Response({
                'summary': call.analysis.summary,
                'structured_data': call.analysis.structured_data,
                'success_evaluation': call.analysis.success_evaluation
            })
        return Response({'summary': '', 'structured_data': {}, 'success_evaluation': ''})


@method_decorator(csrf_exempt, name='dispatch')
class VapiWebhookViewSet(viewsets.ViewSet):
    permission_classes = []
    
    def create(self, request):
        business_slug = request.headers.get('X-Business-Slug')
        if not business_slug:
            logger.error("Missing X-Business-Slug header in webhook request")
            return Response({'error': 'Business slug required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            business = Business.objects.get(slug=business_slug)
        except Business.DoesNotExist:
            logger.error(f"Business not found: {business_slug}")
            return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)
        
        security_manager = WebhookSecurityManager(business)
        if not security_manager.validate_request(request, request.body):
            logger.error(f"Security validation failed for business {business_slug}")
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        processor = WebhookProcessor(business)
        result = processor.process_webhook(request.data)
        
        if result['status'] == 'success':
            logger.info(f"Webhook processed successfully for business {business_slug}")
            return Response(result, status=status.HTTP_200_OK)
        else:
            logger.error(f"Webhook processing failed for business {business_slug}: {result}")
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
