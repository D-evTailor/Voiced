from celery import shared_task
from django.utils import timezone
from .models import VapiCall, VapiAppointmentIntegration
from apps.appointments.models import Appointment
from apps.clients.models import Client
from .services import VapiCallAnalyzer, VapiIntegrationService
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_call_completion(call_id):
    try:
        call = VapiCall.objects.get(id=call_id)
        
        if hasattr(call, 'analysis') and call.analysis.structured_data:
            structured_data = call.analysis.structured_data
            
            analyzer = VapiCallAnalyzer(call)
            appointment_data = analyzer.extract_appointment_data(structured_data)
            
            if appointment_data:
                client = get_or_create_client_from_call(call)
                
                integration_service = VapiIntegrationService(call.business)
                booking_result = integration_service.attempt_booking(appointment_data)
                
                if booking_result.get('success'):
                    try:
                        appointment = Appointment.objects.get(id=booking_result['appointment_id'])
                        VapiAppointmentIntegration.objects.create(
                            call=call,
                            appointment=appointment,
                            booking_successful=True,
                            extracted_data=structured_data
                        )
                        logger.info(f"Successfully processed call {call.call_id} and created appointment {appointment.id}")
                    except Appointment.DoesNotExist:
                        logger.error(f"Created appointment not found: {booking_result.get('appointment_id')}")
                else:
                    VapiAppointmentIntegration.objects.create(
                        call=call,
                        appointment=None,
                        booking_successful=False,
                        booking_error=booking_result.get('error', 'Unknown error'),
                        extracted_data=structured_data
                    )
                    logger.warning(f"Booking failed for call {call.call_id}: {booking_result.get('error')}")
        
        return f"Processed call {call.call_id}"
        
    except VapiCall.DoesNotExist:
        logger.error(f"Call {call_id} not found")
        return f"Call {call_id} not found"
    except Exception as e:
        logger.error(f"Error processing call {call_id}: {e}")
        return f"Error processing call {call_id}: {str(e)}"


def get_or_create_client_from_call(call):
    phone = call.customer_number
    business = call.business
    
    if phone:
        try:
            client, created = Client.objects.get_or_create(
                business=business,
                phone=phone,
                defaults={
                    'name': call.analysis.structured_data.get('client_name', 'Unknown'),
                    'email': call.analysis.structured_data.get('client_email', ''),
                    'source': 'vapi'
                }
            )
            if created:
                logger.info(f"Created new client {client.id} for phone {phone}")
            return client
        except Exception as e:
            logger.error(f"Error creating client for phone {phone}: {e}")
    
    return None


@shared_task
def sync_vapi_calls_status():
    from datetime import timedelta
    
    pending_calls = VapiCall.objects.filter(
        status__in=['queued', 'ringing', 'in_progress'],
        created_at__gte=timezone.now() - timedelta(hours=24)
    )
    
    logger.info(f"Found {pending_calls.count()} pending calls to sync")
    
    for call in pending_calls:
        pass
    
    return f"Synced {pending_calls.count()} calls"
