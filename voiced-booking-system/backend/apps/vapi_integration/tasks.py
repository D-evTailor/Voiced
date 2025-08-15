from celery import shared_task
from django.utils import timezone
from django.db import models
from django.db.models import Sum, Count, Q
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


@shared_task
def calculate_daily_usage_metrics(date_str: str = None):
    from datetime import date, datetime
    from decimal import Decimal
    from django.db.models import Sum, Count
    from apps.businesses.models import Business
    from .models import VapiUsageMetrics
    
    target_date = datetime.fromisoformat(date_str).date() if date_str else date.today()
    
    businesses_with_vapi = Business.objects.filter(
        vapi_configurations__is_active=True
    ).distinct()
    
    for business in businesses_with_vapi:
        calls_data = VapiCall.objects.filter(
            business=business,
            created_at__date=target_date
        ).aggregate(
            total_calls=Count('id'),
            total_minutes=Sum('cost_breakdown__duration_minutes'),
            estimated_cost=Sum('cost')
        )
        
        function_calls_count = VapiCall.objects.filter(
            business=business,
            created_at__date=target_date
        ).aggregate(
            function_calls=Count('id')  # TODO: Count actual function calls from logs
        )['function_calls'] or 0
        
        bookings_data = VapiCall.objects.filter(
            business=business,
            created_at__date=target_date,
            appointment_integration__isnull=False
        ).aggregate(
            successful=Count('id', filter=Q(appointment_integration__booking_successful=True)),
            failed=Count('id', filter=Q(appointment_integration__booking_successful=False))
        )
        
        VapiUsageMetrics.objects.update_or_create(
            business=business,
            date=target_date,
            defaults={
                'total_calls': calls_data['total_calls'] or 0,
                'total_minutes': calls_data['total_minutes'] or Decimal('0'),
                'total_function_calls': function_calls_count,
                'successful_bookings': bookings_data['successful'] or 0,
                'failed_bookings': bookings_data['failed'] or 0,
                'estimated_cost': calls_data['estimated_cost'] or Decimal('0')
            }
        )
    
    logger.info(f"Calculated usage metrics for {businesses_with_vapi.count()} businesses for {target_date}")
    return f"Processed {businesses_with_vapi.count()} businesses"


@shared_task
def generate_monthly_billing_report(business_id: int, year: int, month: int):
    from calendar import monthrange
    from datetime import date
    from apps.businesses.models import Business
    from .models import VapiUsageMetrics
    
    try:
        business = Business.objects.get(id=business_id)
        start_date = date(year, month, 1)
        end_date = date(year, month, monthrange(year, month)[1])
        
        metrics = VapiUsageMetrics.objects.filter(
            business=business,
            date__range=[start_date, end_date]
        ).aggregate(
            total_calls=Sum('total_calls'),
            total_minutes=Sum('total_minutes'),
            total_function_calls=Sum('total_function_calls'),
            successful_bookings=Sum('successful_bookings'),
            failed_bookings=Sum('failed_bookings'),
            estimated_cost=Sum('estimated_cost')
        )
        
        report = {
            'business_id': business.id,
            'business_name': business.name,
            'period': f"{year}-{month:02d}",
            'metrics': metrics,
            'daily_breakdown': list(
                VapiUsageMetrics.objects.filter(
                    business=business,
                    date__range=[start_date, end_date]
                ).values('date', 'total_calls', 'total_minutes', 'estimated_cost')
            )
        }
        
        logger.info(f"Generated billing report for {business.name} - {year}-{month:02d}")
        return report
        
    except Business.DoesNotExist:
        logger.error(f"Business {business_id} not found for billing report")
        return {'error': 'Business not found'}
    except Exception as e:
        logger.error(f"Error generating billing report for business {business_id}: {e}")
        return {'error': str(e)}
