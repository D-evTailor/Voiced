from typing import Dict, List, Optional
from django.utils import timezone
from datetime import datetime, timedelta
from apps.services.models import Service
from apps.resources.models import Resource
from apps.appointments.models import Appointment


class VapiBookingService:
    def __init__(self, business):
        self.business = business
    
    def get_available_services(self) -> List[Dict]:
        services = Service.objects.filter(
            business=self.business,
            is_active=True
        ).values('id', 'name', 'description', 'duration', 'price')
        
        return list(services)
    
    def check_availability(self, service_id: int, requested_date: str, duration_minutes: int = None) -> Dict:
        try:
            service = Service.objects.get(id=service_id, business=self.business)
            date_obj = datetime.fromisoformat(requested_date).date()
            
            if duration_minutes is None:
                duration_minutes = service.duration
            
            available_slots = self._find_available_slots(service, date_obj, duration_minutes)
            
            return {
                'available': len(available_slots) > 0,
                'slots': available_slots,
                'service_name': service.name,
                'duration': duration_minutes
            }
        except Service.DoesNotExist:
            return {'available': False, 'error': 'Service not found'}
        except ValueError:
            return {'available': False, 'error': 'Invalid date format'}
    
    def _find_available_slots(self, service: Service, date_obj, duration_minutes: int) -> List[str]:
        start_time = timezone.datetime.combine(date_obj, timezone.datetime.min.time().replace(hour=9))
        end_time = timezone.datetime.combine(date_obj, timezone.datetime.min.time().replace(hour=18))
        
        existing_appointments = Appointment.objects.filter(
            business=self.business,
            service=service,
            start_time__date=date_obj,
            status__in=['confirmed', 'in_progress']
        ).values_list('start_time', 'end_time')
        
        slots = []
        current_time = start_time
        slot_duration = timedelta(minutes=duration_minutes)
        
        while current_time + slot_duration <= end_time:
            slot_end = current_time + slot_duration
            
            is_available = not any(
                (current_time < end and slot_end > start)
                for start, end in existing_appointments
            )
            
            if is_available:
                slots.append(current_time.isoformat())
            
            current_time += timedelta(minutes=30)
        
        return slots
    
    def create_appointment(self, appointment_data: Dict) -> Dict:
        try:
            service = Service.objects.get(
                id=appointment_data['service_id'],
                business=self.business
            )
            
            start_time = datetime.fromisoformat(appointment_data['start_time'])
            
            if self._is_slot_available(service, start_time, service.duration):
                appointment = Appointment.objects.create(
                    business=self.business,
                    service=service,
                    start_time=start_time,
                    source='vapi',
                    customer_name=appointment_data.get('customer_name', ''),
                    customer_phone=appointment_data.get('customer_phone', ''),
                    customer_email=appointment_data.get('customer_email', ''),
                    client_notes=appointment_data.get('notes', ''),
                    status='confirmed'
                )
                
                return {
                    'success': True,
                    'appointment_id': appointment.id,
                    'booking_reference': appointment.booking_reference,
                    'message': f'Appointment booked for {start_time.strftime("%Y-%m-%d at %H:%M")}'
                }
            else:
                return {
                    'success': False,
                    'error': 'Time slot not available'
                }
                
        except Service.DoesNotExist:
            return {'success': False, 'error': 'Service not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _is_slot_available(self, service: Service, start_time: datetime, duration_minutes: int) -> bool:
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        conflicting = Appointment.objects.filter(
            business=self.business,
            service=service,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=['confirmed', 'in_progress']
        ).exists()
        
        return not conflicting


class VapiCallAnalyzer:
    def __init__(self, call):
        self.call = call
    
    def extract_booking_intent(self, transcript: str) -> Dict:
        booking_keywords = [
            'book', 'appointment', 'schedule', 'reserve', 'cita', 'reservar'
        ]
        
        intent_score = sum(1 for keyword in booking_keywords if keyword.lower() in transcript.lower())
        
        return {
            'has_booking_intent': intent_score > 0,
            'confidence': min(intent_score / len(booking_keywords), 1.0),
            'keywords_found': [kw for kw in booking_keywords if kw.lower() in transcript.lower()]
        }
    
    def extract_appointment_data(self, structured_data: Dict) -> Optional[Dict]:
        if not structured_data:
            return None
        
        appointment_info = {}
        
        if 'service' in structured_data:
            appointment_info['service_name'] = structured_data['service']
        
        if 'date' in structured_data and 'time' in structured_data:
            try:
                date_str = f"{structured_data['date']} {structured_data['time']}"
                appointment_info['datetime'] = datetime.strptime(date_str, '%Y-%m-%d %H:%M').isoformat()
            except ValueError:
                pass
        
        if 'name' in structured_data:
            appointment_info['client_name'] = structured_data['name']
        
        if 'phone' in structured_data:
            appointment_info['client_phone'] = structured_data['phone']
        
        if 'email' in structured_data:
            appointment_info['client_email'] = structured_data['email']
        
        return appointment_info if appointment_info else None


class VapiIntegrationService:
    def __init__(self, business):
        self.business = business
        self.booking_service = VapiBookingService(business)
    
    def process_webhook_data(self, webhook_data: Dict) -> Dict:
        event = webhook_data.get('event')
        call_data = webhook_data.get('call', {})
        
        if event == 'call.ended':
            return self._process_call_ended(call_data)
        elif event == 'call.started':
            return self._process_call_started(call_data)
        
        return {'status': 'processed', 'action': 'none'}
    
    def _process_call_ended(self, call_data: Dict) -> Dict:
        if call_data.get('analysis', {}).get('structuredData'):
            structured_data = call_data['analysis']['structuredData']
            analyzer = VapiCallAnalyzer(None)
            appointment_data = analyzer.extract_appointment_data(structured_data)
            
            if appointment_data:
                result = self._attempt_booking(appointment_data)
                return {'status': 'processed', 'booking_result': result}
        
        return {'status': 'processed', 'action': 'no_booking_data'}
    
    def _process_call_started(self, call_data: Dict) -> Dict:
        return {'status': 'processed', 'action': 'call_started'}
    
    def _attempt_booking(self, appointment_data: Dict) -> Dict:
        try:
            services = self.booking_service.get_available_services()
            matching_service = None
            
            for service in services:
                if appointment_data.get('service_name', '').lower() in service['name'].lower():
                    matching_service = service
                    break
            
            if not matching_service:
                return {'success': False, 'error': 'Service not found'}
            
            booking_data = {
                'service_id': matching_service['id'],
                'start_time': appointment_data.get('datetime'),
                'customer_name': appointment_data.get('client_name', ''),
                'customer_phone': appointment_data.get('client_phone', ''),
                'customer_email': appointment_data.get('client_email', ''),
            }
            
            return self.booking_service.create_appointment(booking_data)
            
        except Exception as e:
            return {'success': False, 'error': f'Booking failed: {str(e)}'}
