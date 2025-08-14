from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.core.permissions import IsBusinessMember
from apps.businesses.models import Business
from .models import VapiConfiguration, VapiCall
from .serializers import (
    VapiConfigurationSerializer, VapiCallSerializer, 
    VapiCallCreateSerializer, VapiWebhookSerializer
)


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
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def webhook(self, request):
        business_slug = request.headers.get('X-Business-Slug')
        if not business_slug:
            return Response({'error': 'Business slug required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            business = Business.objects.get(slug=business_slug)
        except Business.DoesNotExist:
            return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = VapiWebhookSerializer(data=request.data, context={'business': business})
        if serializer.is_valid():
            call = serializer.save()
            return Response({'call_id': call.call_id}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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


class VapiWebhookViewSet(viewsets.ViewSet):
    permission_classes = []
    
    def create(self, request):
        business_slug = request.headers.get('X-Business-Slug')
        if not business_slug:
            return Response({'error': 'Business slug required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            business = Business.objects.get(slug=business_slug)
        except Business.DoesNotExist:
            return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = VapiWebhookSerializer(data=request.data, context={'business': business})
        if serializer.is_valid():
            call = serializer.save()
            
            if request.data.get('event') == 'call.ended':
                from .tasks import process_call_completion
                process_call_completion.delay(call.id)
            
            return Response({'status': 'success', 'call_id': call.call_id}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
