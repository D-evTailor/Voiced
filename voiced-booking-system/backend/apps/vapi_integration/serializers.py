from rest_framework import serializers
from .models import VapiConfiguration, VapiCall, VapiCallTranscript, VapiCallAnalysis, VapiAppointmentIntegration
import logging

logger = logging.getLogger(__name__)


class VapiConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VapiConfiguration
        fields = [
            'id', 'business', 'phone_number_id', 'assistant_id', 'assistant_name',
            'language', 'server_url', 'server_secret', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VapiCallTranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = VapiCallTranscript
        fields = ['transcript', 'messages']


class VapiCallAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = VapiCallAnalysis
        fields = ['summary', 'structured_data', 'success_evaluation']


class VapiAppointmentIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VapiAppointmentIntegration
        fields = ['appointment', 'booking_successful', 'booking_error', 'extracted_data']


class VapiCallSerializer(serializers.ModelSerializer):
    transcript = VapiCallTranscriptSerializer(read_only=True)
    analysis = VapiCallAnalysisSerializer(read_only=True)
    appointment_integration = VapiAppointmentIntegrationSerializer(read_only=True)
    duration_seconds = serializers.ReadOnlyField()
    
    class Meta:
        model = VapiCall
        fields = [
            'id', 'business', 'call_id', 'org_id', 'type', 'status', 'ended_reason',
            'started_at', 'ended_at', 'cost', 'cost_breakdown', 'phone_number',
            'customer_number', 'duration_seconds', 'transcript', 'analysis',
            'appointment_integration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'duration_seconds']


class VapiWebhookSerializer(serializers.Serializer):
    message = serializers.DictField()
    
    def create(self, validated_data):
        message_data = validated_data['message']
        business = self.context['business']
        
        call_data = message_data.get('call', {})
        if not call_data:
            raise serializers.ValidationError("Call data is required")
        
        try:
            call, created = VapiCall.objects.get_or_create(
                call_id=call_data['id'],
                defaults={
                    'business': business,
                    'org_id': call_data.get('orgId', ''),
                    'type': call_data.get('type', ''),
                    'status': call_data.get('status', ''),
                    'ended_reason': call_data.get('endedReason', ''),
                    'started_at': self._parse_datetime(call_data.get('startedAt')),
                    'ended_at': self._parse_datetime(call_data.get('endedAt')),
                    'cost': call_data.get('cost'),
                    'cost_breakdown': call_data.get('costBreakdown', {}),
                    'phone_number': call_data.get('phoneNumber', ''),
                    'customer_number': call_data.get('customer', {}).get('number', ''),
                    'assistant_id': call_data.get('assistantId', ''),
                    'squad_id': call_data.get('squadId', ''),
                    'phone_call_provider': call_data.get('phoneCallProvider', ''),
                    'phone_call_transport': call_data.get('phoneCallTransport', ''),
                }
            )
            
            if not created:
                self._update_call_fields(call, call_data)
            
            self._update_transcript(call, call_data)
            self._update_analysis(call, call_data)
            
            if created:
                logger.info(f"Created new call: {call.call_id}")
            else:
                logger.info(f"Updated existing call: {call.call_id}")
            
            return call
            
        except Exception as e:
            logger.error(f"Error creating/updating call {call_data.get('id')}: {e}")
            raise serializers.ValidationError(f"Error processing call data: {str(e)}")
    
    def _parse_datetime(self, dt_str):
        if not dt_str:
            return None
        try:
            from django.utils.dateparse import parse_datetime
            return parse_datetime(dt_str)
        except Exception:
            return None
    
    def _update_call_fields(self, call, call_data):
        update_fields = []
        
        for field, key in [
            ('status', 'status'),
            ('ended_reason', 'endedReason'),
            ('cost', 'cost'),
            ('ended_at', 'endedAt'),
        ]:
            if key in call_data:
                value = call_data[key]
                if field == 'ended_at':
                    value = self._parse_datetime(value)
                if getattr(call, field) != value:
                    setattr(call, field, value)
                    update_fields.append(field)
        
        if update_fields:
            call.save(update_fields=update_fields)
    
    def _update_transcript(self, call, call_data):
        if call_data.get('transcript'):
            VapiCallTranscript.objects.update_or_create(
                call=call,
                defaults={
                    'transcript': call_data['transcript'],
                    'messages': call_data.get('messages', []),
                }
            )
    
    def _update_analysis(self, call, call_data):
        if call_data.get('analysis'):
            analysis_data = call_data['analysis']
            VapiCallAnalysis.objects.update_or_create(
                call=call,
                defaults={
                    'summary': analysis_data.get('summary', ''),
                    'structured_data': analysis_data.get('structuredData', {}),
                    'success_evaluation': analysis_data.get('successEvaluation', ''),
                }
            )
