from abc import ABC, abstractmethod
from typing import Dict, Any
from .value_objects import VapiEventType, CallAnalysisData
from .models import VapiCall
from .domain_services import AvailabilityQueryService, AppointmentBookingDomainService
from .api_client import VapiBusinessService
import logging

logger = logging.getLogger(__name__)


class EventHandler(ABC):
    @abstractmethod
    def can_handle(self, event_type: VapiEventType) -> bool:
        pass
    
    @abstractmethod
    def handle(self, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        pass


class BaseCallEventHandler(EventHandler):
    def _log_event(self, event_type: str, call: VapiCall, details: str = ""):
        logger.info(f"{event_type} event for call {call.call_id} {details}")


class CallStartedHandler(BaseCallEventHandler):
    def can_handle(self, event_type: VapiEventType) -> bool:
        return event_type.is_call_started
    
    def handle(self, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        self._log_event("Call started", call)
        return {'status': 'call_started', 'call_id': call.call_id}


class CallEndedHandler(BaseCallEventHandler):
    def can_handle(self, event_type: VapiEventType) -> bool:
        return event_type.is_call_ended
    
    def handle(self, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        if not hasattr(call, 'analysis') or not call.analysis.structured_data:
            self._log_event("Call ended", call, "without analysis data")
            return {'status': 'no_analysis_data'}
        
        analysis = CallAnalysisData.from_dict({
            'summary': call.analysis.summary,
            'structuredData': call.analysis.structured_data,
            'successEvaluation': call.analysis.success_evaluation
        })
        
        if analysis.has_appointment_data:
            from .tasks import process_call_completion
            process_call_completion.delay(call.id)
            self._log_event("Call ended", call, "with appointment data - scheduled processing")
            return {'status': 'scheduled_processing', 'call_id': call.call_id}
        
        self._log_event("Call ended", call, "without appointment data")
        return {'status': 'no_appointment_data'}


class FunctionCallHandler(BaseCallEventHandler):
    def can_handle(self, event_type: VapiEventType) -> bool:
        return event_type.is_function_call
    
    def handle(self, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        function_call = event_data.get('functionCall', {})
        function_name = function_call.get('name', '')
        parameters = function_call.get('parameters', {})
        
        self._log_event("Function call", call, f"- {function_name}")
        
        try:
            result = self._execute_function(call, function_name, parameters)
            return {
                'status': 'function_executed',
                'result': result,
                'functionCall': {
                    'name': function_name,
                    'result': result
                }
            }
        except Exception as e:
            logger.error(f"Function call failed for {function_name}: {e}")
            return {
                'status': 'function_error',
                'error': str(e),
                'functionCall': {
                    'name': function_name,
                    'error': str(e)
                }
            }
    
    def _execute_function(self, call: VapiCall, function_name: str, parameters: Dict) -> Any:
        if function_name == 'get_available_services':
            service = AvailabilityQueryService(call.business)
            return service.get_available_services()
        
        elif function_name == 'check_availability':
            service = AvailabilityQueryService(call.business)
            return service.check_availability(
                parameters.get('service_id'),
                parameters.get('date'),
                parameters.get('duration')
            )
        
        elif function_name == 'book_appointment':
            booking_service = AppointmentBookingDomainService(call.business)
            from .value_objects import AppointmentBookingData
            
            booking_data = AppointmentBookingData(
                service_name=parameters.get('service_name', ''),
                client_name=parameters.get('client_name', ''),
                client_phone=parameters.get('client_phone', ''),
                client_email=parameters.get('client_email', ''),
                datetime_iso=parameters.get('datetime', ''),
                notes=parameters.get('notes', '')
            )
            
            return booking_service.book_appointment(booking_data)
        
        else:
            raise ValueError(f"Unknown function: {function_name}")


class AssistantRequestHandler(BaseCallEventHandler):
    def can_handle(self, event_type: VapiEventType) -> bool:
        return event_type.is_assistant_request
    
    def handle(self, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        phone_number = event_data.get('call', {}).get('from', {}).get('phoneNumber', '')
        self._log_event("Assistant request", call, f"from {phone_number}")
        
        config = call.business.vapi_configurations.filter(is_active=True).first()
        if not config:
            return {
                'status': 'error',
                'error': 'No active VAPI configuration found'
            }
        
        vapi_service = VapiBusinessService(call.business)
        try:
            assistant_id = vapi_service.get_or_create_assistant()
            return {
                'status': 'assistant_provided',
                'assistantId': assistant_id,
                'assistant': config.assistant_config
            }
        except Exception as e:
            logger.error(f"Failed to get assistant for business {call.business.id}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


class TranscriptHandler(BaseCallEventHandler):
    def can_handle(self, event_type: VapiEventType) -> bool:
        return event_type.is_transcript
    
    def handle(self, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        transcript_data = event_data.get('transcript', {})
        self._log_event("Transcript", call, f"received")
        
        return {'status': 'transcript_processed'}


class EndOfCallReportHandler(BaseCallEventHandler):
    def can_handle(self, event_type: VapiEventType) -> bool:
        return event_type.is_end_of_call_report
    
    def handle(self, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        self._log_event("End of call report", call, "received")
        
        from .tasks import process_call_analysis
        process_call_analysis.delay(call.id, event_data)
        
        return {'status': 'analysis_scheduled'}


class EventHandlerRegistry:
    def __init__(self):
        self._handlers = [
            CallStartedHandler(),
            CallEndedHandler(),
            FunctionCallHandler(),
            AssistantRequestHandler(),
            TranscriptHandler(),
            EndOfCallReportHandler(),
        ]
    
    def handle_event(self, event_type: VapiEventType, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        for handler in self._handlers:
            if handler.can_handle(event_type):
                return handler.handle(call, event_data)
        
        logger.warning(f"No handler found for event type: {event_type.value}")
        return {'status': 'unhandled_event', 'event_type': event_type.value}
