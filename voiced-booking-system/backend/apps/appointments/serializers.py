from rest_framework import serializers
from apps.core.serializers import TenantFilteredSerializer, BaseSerializer, TimeFieldsMixin, DisplayFieldsMixin
from .models import Appointment, Client


class ClientSerializer(TenantFilteredSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = '__all__'
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class AppointmentSerializer(TenantFilteredSerializer, TimeFieldsMixin, DisplayFieldsMixin):
    service_name = serializers.CharField(source='service.name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    duration_display = serializers.CharField(source='service.duration_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'


class AppointmentCreateSerializer(TenantFilteredSerializer):
    client_data = ClientSerializer(required=False, write_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'
        extra_kwargs = {
            'client_data': {'write_only': True}
        }
    
    def create(self, validated_data):
        client_data = validated_data.pop('client_data', None)
        
        if client_data:
            client_serializer = ClientSerializer(data=client_data, context=self.context)
            client_serializer.is_valid(raise_exception=True)
            client = client_serializer.save()
            validated_data['client'] = client
        
        return super().create(validated_data)


class AppointmentListSerializer(serializers.ModelSerializer, TimeFieldsMixin, DisplayFieldsMixin):
    service_name = serializers.CharField(source='service.name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'service_name', 'client_name', 'start_time', 'end_time', 
                 'status', 'status_display', 'created_at']
