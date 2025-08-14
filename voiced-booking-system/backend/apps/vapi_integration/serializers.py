from rest_framework import serializers
from .models import VapiConfiguration, VapiCall, VapiCallTranscript, VapiCallAnalysis, VapiAppointmentIntegration


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


class VapiCallCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VapiCall
        fields = [
            'call_id', 'org_id', 'type', 'status', 'ended_reason',
            'started_at', 'ended_at', 'cost', 'cost_breakdown',
            'phone_number', 'customer_number'
        ]


class VapiWebhookSerializer(serializers.Serializer):
    event = serializers.CharField()
    call = serializers.DictField()
    timestamp = serializers.DateTimeField()
    
    def create(self, validated_data):
        call_data = validated_data['call']
        business = self.context['business']
        
        call, created = VapiCall.objects.get_or_create(
            call_id=call_data['id'],
            defaults={
                'business': business,
                'org_id': call_data.get('orgId', ''),
                'type': call_data.get('type', ''),
                'status': call_data.get('status', ''),
                'ended_reason': call_data.get('endedReason', ''),
                'started_at': call_data.get('startedAt'),
                'ended_at': call_data.get('endedAt'),
                'cost': call_data.get('cost'),
                'cost_breakdown': call_data.get('costBreakdown', {}),
                'phone_number': call_data.get('phoneNumber', ''),
                'customer_number': call_data.get('customer', {}).get('number', ''),
            }
        )
        
        if call_data.get('transcript'):
            VapiCallTranscript.objects.update_or_create(
                call=call,
                defaults={
                    'transcript': call_data['transcript'],
                    'messages': call_data.get('messages', []),
                }
            )
        
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
        
        return call
