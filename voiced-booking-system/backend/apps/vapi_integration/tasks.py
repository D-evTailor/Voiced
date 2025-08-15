from celery import shared_task
from django.utils import timezone
from .models import VapiCall, VapiAppointmentIntegration, VapiCallAnalysis
from apps.appointments.models import Appointment
from .domain_services import CallAnalysisDomainService, AppointmentBookingDomainService
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_call_completion(call_id):
    try:
        call = VapiCall.objects.get(id=call_id)
        
        if hasattr(call, 'analysis') and call.analysis.structured_data:
            analysis_service = CallAnalysisDomainService()
            booking_data = analysis_service.extract_booking_data(call.analysis.structured_data)
            
            if booking_data and booking_data.is_valid:
                booking_service = AppointmentBookingDomainService(call.business)
                booking_result = booking_service.book_appointment(booking_data)
                
                if booking_result.get('success'):
                    try:
                        appointment = Appointment.objects.get(id=booking_result['appointment_id'])
                        VapiAppointmentIntegration.objects.create(
                            call=call,
                            appointment=appointment,
                            booking_successful=True,
                            extracted_data=call.analysis.structured_data
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
                        extracted_data=call.analysis.structured_data
                    )
                    logger.warning(f"Booking failed for call {call.call_id}: {booking_result.get('error')}")
            else:
                logger.info(f"No valid booking data for call {call.call_id}")
        
        return f"Processed call {call.call_id}"
        
    except VapiCall.DoesNotExist:
        logger.error(f"Call {call_id} not found")
        return f"Call {call_id} not found"
    except Exception as e:
        logger.error(f"Error processing call {call_id}: {e}")
        return f"Error processing call {call_id}: {str(e)}"


@shared_task
def process_call_analysis(call_id, analysis_data):
    try:
        call = VapiCall.objects.get(id=call_id)
        
        analysis, created = VapiCallAnalysis.objects.update_or_create(
            call=call,
            defaults={
                'summary': analysis_data.get('summary', ''),
                'structured_data': analysis_data.get('structuredData', {}),
                'success_evaluation': analysis_data.get('successEvaluation', ''),
            }
        )
        
        if created:
            logger.info(f"Created analysis for call {call.call_id}")
        else:
            logger.info(f"Updated analysis for call {call.call_id}")
        
        return f"Analysis processed for call {call.call_id}"
        
    except VapiCall.DoesNotExist:
        logger.error(f"Call {call_id} not found for analysis")
        return f"Call {call_id} not found"
    except Exception as e:
        logger.error(f"Error processing analysis for call {call_id}: {e}")
        return f"Error processing analysis: {str(e)}"


@shared_task
def cleanup_old_call_data():
    from datetime import timedelta
    
    old_calls = VapiCall.objects.filter(
        created_at__lt=timezone.now() - timedelta(days=90),
        status='ended'
    )
    
    count = old_calls.count()
    old_calls.delete()
    
    logger.info(f"Cleaned up {count} old calls")
    return f"Cleaned up {count} old calls"


@shared_task
def register_tenant_async(business_id: int, area_code: str = None):
    from .multi_tenant_services import TenantRegistrationService
    from apps.businesses.models import Business
    
    try:
        business = Business.objects.get(id=business_id)
        service = TenantRegistrationService()
        result = service.register_tenant(business, area_code)
        
        if result['success']:
            logger.info(f"Async tenant registration completed for {business.name}")
        else:
            logger.error(f"Async tenant registration failed for {business.name}: {result.get('error')}")
        
        return result
        
    except Business.DoesNotExist:
        logger.error(f"Business {business_id} not found for async registration")
        return {'success': False, 'error': 'Business not found'}
    except Exception as e:
        logger.error(f"Async tenant registration error for business {business_id}: {e}")
        return {'success': False, 'error': str(e)}
