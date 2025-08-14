from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.views import APIView
from datetime import datetime, timedelta
from django.utils import timezone
from apps.core.viewsets import TenantViewSet
from apps.core.permissions import BusinessStaffPermission
from apps.core.exceptions import success_response, error_response
from .models import Appointment, Client
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer, AppointmentListSerializer,
    ClientSerializer
)


class ClientViewSet(TenantViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated, BusinessStaffPermission]
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    filterset_fields = ['email', 'phone']
    ordering = ['first_name', 'last_name']
    
    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        client = self.get_object()
        appointments = client.appointments.all()
        serializer = AppointmentListSerializer(appointments, many=True)
        return success_response(data=serializer.data)


class AppointmentViewSet(TenantViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, BusinessStaffPermission]
    filterset_fields = ['service', 'client', 'status', 'start_time__date']
    ordering = ['-start_time']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentCreateSerializer
        elif self.action == 'list':
            return AppointmentListSerializer
        return AppointmentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(start_time__gte=date_from)
        if date_to:
            queryset = queryset.filter(start_time__lte=date_to)
            
        return queryset
    
    @action(detail=True, methods=['patch'])
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'confirmed'
        appointment.save()
        return success_response(
            data={'status': appointment.status},
            message="Appointment confirmed"
        )
    
    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'cancelled'
        appointment.cancellation_reason = request.data.get('reason', '')
        appointment.save()
        return success_response(
            data={'status': appointment.status},
            message="Appointment cancelled"
        )
    
    @action(detail=True, methods=['patch'])
    def complete(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'completed'
        appointment.end_time = timezone.now()
        appointment.save()
        return success_response(
            data={'status': appointment.status},
            message="Appointment completed"
        )
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        appointments = self.get_queryset().filter(start_time__date=today)
        serializer = AppointmentListSerializer(appointments, many=True)
        return success_response(data=serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        now = timezone.now()
        appointments = self.get_queryset().filter(
            start_time__gte=now,
            status__in=['scheduled', 'confirmed']
        )[:10]
        serializer = AppointmentListSerializer(appointments, many=True)
        return success_response(data=serializer.data)


class AvailabilityView(APIView):
    permission_classes = [permissions.IsAuthenticated, BusinessStaffPermission]
    
    def get(self, request):
        service_id = request.query_params.get('service_id')
        date = request.query_params.get('date')
        
        if not service_id or not date:
            return error_response(message="service_id and date are required")
        
        try:
            from apps.services.models import Service
            service = Service.objects.get(id=service_id, business=request.business)
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
            
            available_slots = self._get_available_slots(service, target_date)
            
            return success_response(data={
                'service_id': service_id,
                'date': date,
                'available_slots': available_slots
            })
            
        except Service.DoesNotExist:
            return error_response(message="Service not found")
        except ValueError:
            return error_response(message="Invalid date format. Use YYYY-MM-DD")
    
    def _get_available_slots(self, service, date):
        start_time = datetime.combine(date, datetime.min.time().replace(hour=9))
        end_time = datetime.combine(date, datetime.min.time().replace(hour=18))
        
        slots = []
        current_time = start_time
        
        while current_time < end_time:
            slot_end = current_time + timedelta(minutes=service.duration)
            
            if not Appointment.objects.filter(
                service=service,
                start_time__lt=slot_end,
                start_time__gte=current_time,
                status__in=['scheduled', 'confirmed']
            ).exists():
                slots.append(current_time.strftime('%H:%M'))
            
            current_time += timedelta(minutes=30)
        
        return slots
