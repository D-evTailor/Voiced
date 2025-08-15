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
from .serializers import VapiConfigurationSerializer, VapiCallSerializer
from .security import WebhookSecurityManager
from .processors import WebhookProcessor
from .api_client import VapiBusinessService
from .value_objects import BusinessSlug
import logging

logger = logging.getLogger(__name__)


class VapiConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = VapiConfigurationSerializer
    permission_classes = [IsAuthenticated, IsBusinessMember]
    
    def get_queryset(self):
        business_id = self.kwargs.get('business_id') or self.request.query_params.get('business_id')
        if business_id:
            business = get_object_or_404(Business, id=business_id)
            return VapiConfiguration.objects.select_related('business').filter(
                business=business, is_active=True
            )
        return VapiConfiguration.objects.none()
    
    def perform_create(self, serializer):
        business_id = self.kwargs.get('business_id') or self.request.data.get('business_id')
        business = get_object_or_404(Business, id=business_id)
        serializer.save(business=business)
    
    @action(detail=False, methods=['post'])
    def register_tenant(self, request):
        from .multi_tenant_services import TenantRegistrationService
        
        business_id = request.data.get('business_id')
        if not business_id:
            return Response({
                'error': 'Business ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            business = Business.objects.get(id=business_id)
            service = TenantRegistrationService()
            result = service.register_tenant(
                business=business,
                area_code=request.data.get('area_code')
            )
            
            if result['success']:
                logger.info(f"Tenant registered successfully: {business.name}")
                return Response(result)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Business.DoesNotExist:
            return Response({
                'error': 'Business not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Tenant registration failed: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VapiCallViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VapiCallSerializer
    permission_classes = [IsAuthenticated, IsBusinessMember]
    
    def get_queryset(self):
        business_id = self.kwargs.get('business_id') or self.request.query_params.get('business_id')
        if business_id:
            business = get_object_or_404(Business, id=business_id)
            return VapiCall.objects.filter(business=business).select_related(
                'business', 'transcript', 'analysis'
            ).prefetch_related('appointment_integration__appointment')
        return VapiCall.objects.none()
    
    @action(detail=False, methods=['post'])
    def make_outbound_call(self, request):
        from .multi_tenant_services import SharedAgentManager
        from .api_client import VapiAPIClient
        
        business_id = self.kwargs.get('business_id') or request.data.get('business_id')
        business = get_object_or_404(Business, id=business_id)
        
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({
                'error': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            config = business.vapi_configurations.filter(is_active=True).first()
            if not config:
                return Response({
                    'error': 'No VAPI configuration found for business'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            shared_agent = SharedAgentManager()
            client = VapiAPIClient()
            
            result = client.create_phone_call(
                phone_number=phone_number,
                assistant_id=shared_agent.shared_agent_id,
                phone_number_id=config.phone_number_id,
                metadata={'tenant_id': str(business.id), 'business_slug': business.slug}
            )
            
            logger.info(f"Outbound call initiated for business {business.id} to {phone_number}")
            return Response({
                'success': True,
                'call_id': result.get('id'),
                'status': result.get('status'),
                'message': 'Outbound call initiated successfully'
            })
        except Exception as e:
            logger.error(f"Outbound call failed for business {business.id}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
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
        processor = WebhookProcessor()
        result = processor.process_webhook(request.data)
        
        if 'error' in result:
            logger.error(f"Webhook processing failed: {result}")
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.info("Webhook processed successfully")
            return Response(result, status=status.HTTP_200_OK)
