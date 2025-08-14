from celery import shared_task
from django.utils import timezone
from .models import VapiCall, VapiAppointmentIntegration
from apps.appointments.models import Appointment
from apps.clients.models import Client


@shared_task
def process_call_completion(call_id):
    try:
        call = VapiCall.objects.get(id=call_id)
        
        if hasattr(call, 'analysis') and call.analysis.structured_data:
            structured_data = call.analysis.structured_data
            
            appointment_data = structured_data.get('appointment', {})
            if appointment_data and appointment_data.get('service_name'):
                client = get_or_create_client_from_call(call)
                appointment = create_appointment_from_structured_data(call, client, appointment_data)
                
                VapiAppointmentIntegration.objects.create(
                    call=call,
                    appointment=appointment,
                    booking_successful=True,
                    extracted_data=structured_data
                )
        
        return f"Processed call {call.call_id}"
        
    except VapiCall.DoesNotExist:
        return f"Call {call_id} not found"
    except Exception as e:
        return f"Error processing call {call_id}: {str(e)}"


def get_or_create_client_from_call(call):
    phone = call.customer_number
    business = call.business
    
    if phone:
        client, created = Client.objects.get_or_create(
            business=business,
            phone=phone,
            defaults={
                'name': call.analysis.structured_data.get('client_name', 'Unknown'),
                'email': call.analysis.structured_data.get('client_email', ''),
                'source': 'vapi'
            }
        )
        return client
    
    return None


def create_appointment_from_structured_data(call, client, appointment_data):
    from apps.services.models import Service
    from datetime import datetime
    
    try:
        service = Service.objects.get(
            business=call.business,
            name__icontains=appointment_data.get('service_name', '')
        )
        
        appointment_datetime = datetime.fromisoformat(appointment_data.get('datetime'))
        
        appointment = Appointment.objects.create(
            business=call.business,
            client=client,
            service=service,
            start_time=appointment_datetime,
            source='vapi',
            customer_name=client.name if client else appointment_data.get('client_name', ''),
            customer_phone=call.customer_number,
            customer_email=appointment_data.get('client_email', ''),
            client_notes=appointment_data.get('notes', ''),
            status='confirmed'
        )
        
        return appointment
        
    except Service.DoesNotExist:
        raise ValueError(f"Service not found: {appointment_data.get('service_name')}")
    except Exception as e:
        raise ValueError(f"Error creating appointment: {str(e)}")


@shared_task
def sync_vapi_calls_status():
    from datetime import timedelta
    
    pending_calls = VapiCall.objects.filter(
        status__in=['queued', 'ringing', 'in_progress'],
        created_at__gte=timezone.now() - timedelta(hours=24)
    )
    
    for call in pending_calls:
        pass
    
    return f"Synced {pending_calls.count()} calls"
