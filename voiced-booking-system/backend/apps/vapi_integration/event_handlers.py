from abc import ABC, abstractmethod
from typing import Dict, Any
from .value_objects import VapiEventType, CallAnalysisData
from .models import VapiCall
import logging

logger = logging.getLogger(__name__)


class EventHandler(ABC):
    @abstractmethod
    def can_handle(self, event_type: VapiEventType) -> bool:
        pass
    
    @abstractmethod
    def handle(self, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        pass


class CallStartedHandler(EventHandler):
    def can_handle(self, event_type: VapiEventType) -> bool:
        return event_type.is_call_started
    
    def handle(self, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Call started: {call.call_id}")
        return {'action': 'call_started', 'call_id': call.call_id}


class CallEndedHandler(EventHandler):
    def can_handle(self, event_type: VapiEventType) -> bool:
        return event_type.is_call_ended
    
    def handle(self, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        if not hasattr(call, 'analysis') or not call.analysis.structured_data:
            logger.info(f"Call ended without analysis data: {call.call_id}")
            return {'action': 'no_analysis_data'}
        
        analysis = CallAnalysisData.from_dict({
            'summary': call.analysis.summary,
            'structuredData': call.analysis.structured_data,
            'successEvaluation': call.analysis.success_evaluation
        })
        
        if analysis.has_appointment_data:
            from .tasks import process_call_completion
            process_call_completion.delay(call.id)
            logger.info(f"Scheduled appointment processing for call: {call.call_id}")
            return {'action': 'scheduled_processing', 'call_id': call.call_id}
        
        logger.info(f"Call ended without appointment data: {call.call_id}")
        return {'action': 'no_appointment_data'}


class ToolCallHandler(EventHandler):
    def can_handle(self, event_type: VapiEventType) -> bool:
        return event_type.is_tool_call
    
    def handle(self, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        tool_call = event_data.get('tool_call', {})
        tool_name = tool_call.get('function', {}).get('name', '')
        
        logger.info(f"Tool call received: {tool_name} for call {call.call_id}")
        
        from .domain_services import AvailabilityQueryService
        service = AvailabilityQueryService(call.business)
        
        if tool_name == 'get_available_services':
            result = service.get_available_services()
            return {'action': 'tool_response', 'result': result}
        
        elif tool_name == 'check_availability':
            params = tool_call.get('function', {}).get('arguments', {})
            result = service.check_availability(
                params.get('service_id'),
                params.get('date'),
                params.get('duration')
            )
            return {'action': 'tool_response', 'result': result}
        
        return {'action': 'unknown_tool', 'tool_name': tool_name}


class AssistantRequestHandler(EventHandler):
    def can_handle(self, event_type: VapiEventType) -> bool:
        return event_type.is_assistant_request
    
    def handle(self, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        phone_number = event_data.get('call', {}).get('from', {}).get('phoneNumber', '')
        
        logger.info(f"Assistant request for phone: {phone_number}")
        
        config = call.business.vapi_configurations.filter(is_active=True).first()
        if not config:
            return {'action': 'error', 'message': 'No configuration found'}
        
        return {
            'action': 'assistant_response',
            'assistant': {
                'firstMessage': f'Hola, soy el asistente de {call.business.name}. ¿En qué puedo ayudarte?',
                'voice': {'provider': 'openai', 'voiceId': 'nova'},
                'model': {'provider': 'openai', 'model': 'gpt-4o-mini'},
                'serverUrl': config.server_url
            }
        }


class EventHandlerRegistry:
    def __init__(self):
        self._handlers = [
            CallStartedHandler(),
            CallEndedHandler(),
            ToolCallHandler(),
            AssistantRequestHandler()
        ]
    
    def handle_event(self, event_type: VapiEventType, call: VapiCall, event_data: Dict[str, Any]) -> Dict[str, Any]:
        for handler in self._handlers:
            if handler.can_handle(event_type):
                return handler.handle(call, event_data)
        
        logger.warning(f"No handler found for event type: {event_type.value}")
        return {'action': 'unhandled_event', 'event_type': event_type.value}
