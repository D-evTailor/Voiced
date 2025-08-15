from typing import Dict, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from apps.services.models import Service
from apps.appointments.models import Appointment
from apps.clients.models import Client
from .value_objects import AppointmentBookingData
from .optimizations import cached_method, circuit_breaker, cache_service, VapiCacheKeys
import logging

logger = logging.getLogger(__name__)


class BaseBusinessService:
    def __init__(self, business):
        self.business = business


class AppointmentBookingDomainService(BaseBusinessService):
    @circuit_breaker
    def book_appointment(self, booking_data: AppointmentBookingData) -> Dict[str, any]:
        if not booking_data.is_valid:
            return {'success': False, 'error': 'Invalid booking data'}
        
        try:
            with transaction.atomic():
                service = self._find_service(booking_data.service_name)
                if not service:
                    return {'success': False, 'error': 'Service not found'}
                
                start_time = datetime.fromisoformat(booking_data.datetime_iso)
                
                if not self._is_slot_available(service, start_time):
                    return {'success': False, 'error': 'Time slot not available'}
                
                client = self._get_or_create_client(booking_data)
                appointment = self._create_appointment(service, client, booking_data, start_time)
                
                self._invalidate_availability_cache(service, start_time)
                
                logger.info(f"Appointment booked: {appointment.id} for business {self.business.id}")
                return {
                    'success': True,
                    'appointment_id': appointment.id,
                    'booking_reference': appointment.booking_reference
                }
                
        except Exception as e:
            logger.error(f"Booking failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _find_service(self, service_name: str) -> Optional[Service]:
        return Service.objects.select_related('business').filter(
            business=self.business,
            name__icontains=service_name,
            is_active=True
        ).first()
    
    def _is_slot_available(self, service: Service, start_time: datetime) -> bool:
        end_time = start_time + timedelta(minutes=service.duration)
        
        return not Appointment.objects.filter(
            business=self.business,
            service=service,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=['confirmed', 'in_progress']
        ).exists()
    
    def _get_or_create_client(self, booking_data: AppointmentBookingData) -> Optional[Client]:
        if not booking_data.client_phone:
            return None
        
        client, created = Client.objects.get_or_create(
            business=self.business,
            phone=booking_data.client_phone,
            defaults={
                'name': booking_data.client_name or 'Unknown',
                'email': booking_data.client_email,
                'source': 'vapi'
            }
        )
        
        if created:
            logger.info(f"Created client: {client.id}")
        
        return client
    
    def _create_appointment(self, service: Service, client: Optional[Client], 
                          booking_data: AppointmentBookingData, start_time: datetime) -> Appointment:
        return Appointment.objects.create(
            business=self.business,
            service=service,
            client=client,
            start_time=start_time,
            source='vapi',
            customer_name=booking_data.client_name,
            customer_phone=booking_data.client_phone,
            customer_email=booking_data.client_email,
            client_notes=booking_data.notes,
            status='confirmed'
        )
    
    def _invalidate_availability_cache(self, service: Service, start_time: datetime):
        date_str = start_time.date().isoformat()
        cache_service.invalidate_pattern(f"vapi:availability:{self.business.id}:{service.id}:*")


class AvailabilityQueryService(BaseBusinessService):
    @cached_method(timeout=600, key_func=lambda self: VapiCacheKeys.services(self.business.id))
    def get_available_services(self) -> List[Dict]:
        return list(Service.objects.filter(
            business=self.business,
            is_active=True
        ).values('id', 'name', 'description', 'duration', 'price'))
    
    @cached_method(timeout=300)
    def check_availability(self, service_id: int, date: str, duration: Optional[int] = None) -> Dict:
        try:
            service = Service.objects.select_related('business').get(
                id=service_id, business=self.business
            )
            date_obj = datetime.fromisoformat(date).date()
            duration_minutes = duration or service.duration
            
            cache_key = VapiCacheKeys.availability(self.business.id, service_id, date)
            slots = cache_service.get_or_set(
                cache_key,
                lambda: self._find_available_slots(service, date_obj, duration_minutes),
                timeout=900
            )
            
            return {
                'available': len(slots) > 0,
                'slots': slots,
                'service_name': service.name,
                'duration': duration_minutes
            }
        except Service.DoesNotExist:
            return {'available': False, 'error': 'Service not found'}
        except ValueError:
            return {'available': False, 'error': 'Invalid date format'}
    
    def _find_available_slots(self, service: Service, date_obj, duration_minutes: int) -> List[str]:
        business_hours = self._get_business_hours(date_obj)
        if not business_hours:
            return []
        
        start_time, end_time = business_hours
        existing_appointments = self._get_existing_appointments(service, date_obj)
        
        return self._calculate_available_slots(start_time, end_time, duration_minutes, existing_appointments)
    
    def _get_business_hours(self, date_obj) -> Optional[tuple]:
        day_of_week = date_obj.weekday()
        hours = self.business.business_hours.filter(day_of_week=day_of_week, is_closed=False).first()
        
        if not hours or not hours.open_time or not hours.close_time:
            return None
        
        start_time = timezone.datetime.combine(date_obj, hours.open_time)
        end_time = timezone.datetime.combine(date_obj, hours.close_time)
        
        return start_time, end_time
    
    def _get_existing_appointments(self, service: Service, date_obj):
        return Appointment.objects.filter(
            business=self.business,
            service=service,
            start_time__date=date_obj,
            status__in=['confirmed', 'in_progress']
        ).values_list('start_time', 'end_time')
    
    def _calculate_available_slots(self, start_time, end_time, duration_minutes: int, existing_appointments) -> List[str]:
        slots = []
        current_time = start_time
        slot_duration = timedelta(minutes=duration_minutes)
        slot_interval = timedelta(minutes=30)
        
        while current_time + slot_duration <= end_time:
            slot_end = current_time + slot_duration
            
            is_available = not any(
                (current_time < existing_end and slot_end > existing_start)
                for existing_start, existing_end in existing_appointments
            )
            
            if is_available:
                slots.append(current_time.isoformat())
            
            current_time += slot_interval
        
        return slots


class CallAnalysisDomainService:
    def extract_booking_data(self, structured_data: Dict) -> Optional[AppointmentBookingData]:
        if not structured_data:
            return None
        
        try:
            return AppointmentBookingData.from_structured_data(structured_data)
        except Exception as e:
            logger.error(f"Error extracting booking data: {e}")
            return None
