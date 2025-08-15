from typing import Dict
from django.db import transaction
from .models import VapiCall
from .serializers import VapiWebhookSerializer
from .value_objects import VapiEventType
from .event_handlers import EventHandlerRegistry
import logging

logger = logging.getLogger(__name__)


class WebhookProcessor:
    def __init__(self, business):
        self.business = business
        self.event_registry = EventHandlerRegistry()
    
    def process_webhook(self, webhook_data: Dict) -> Dict:
        try:
            event_type = VapiEventType(webhook_data.get('message', {}).get('type', ''))
            
            with transaction.atomic():
                call = self._save_call_data(webhook_data)
                result = self.event_registry.handle_event(event_type, call, webhook_data)
                
                logger.info(f"Processed {event_type.value} event for call {call.call_id}")
                
                return self._format_response(result, call, event_type)
                
        except ValueError as e:
            logger.error(f"Invalid event type: {e}")
            return {'error': f'Invalid event type: {str(e)}'}
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return {'error': f'Processing failed: {str(e)}'}
    
    def _format_response(self, result: Dict, call: VapiCall, event_type: VapiEventType) -> Dict:
        status = result.get('status', 'unknown')
        
        if status == 'function_executed':
            return result.get('functionCall', {})
        
        elif status == 'assistant_provided':
            if 'assistantId' in result:
                return {'assistantId': result['assistantId']}
            else:
                return result.get('assistant', {})
        
        elif status in ('error', 'function_error'):
            return {'error': result.get('error', 'Unknown error')}
        
        return {
            'status': 'success',
            'call_id': call.call_id,
            'event': event_type.value,
            'message': f'Event {event_type.value} processed successfully'
        }
    
    def _save_call_data(self, webhook_data: Dict) -> VapiCall:
        serializer = VapiWebhookSerializer(
            data=webhook_data,
            context={'business': self.business}
        )
        serializer.is_valid(raise_exception=True)
        return serializer.save()
