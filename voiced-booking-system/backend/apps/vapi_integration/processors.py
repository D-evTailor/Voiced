from typing import Dict, Optional
from django.db import transaction
from .models import VapiCall
from .serializers import VapiWebhookSerializer
import logging

logger = logging.getLogger(__name__)


class WebhookProcessor:
    def __init__(self, business):
        self.business = business
    
    def process_webhook(self, webhook_data: Dict) -> Dict:
        event_type = webhook_data.get('event')
        
        try:
            with transaction.atomic():
                call = self._save_call_data(webhook_data)
                result = self._process_event(event_type, call, webhook_data)
                
                logger.info(f"Processed {event_type} event for call {call.call_id}")
                return {
                    'status': 'success',
                    'call_id': call.call_id,
                    'event_processed': event_type,
                    **result
                }
                
        except Exception as e:
            logger.error(f"Error processing webhook {event_type}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'event': event_type
            }
    
    def _save_call_data(self, webhook_data: Dict) -> VapiCall:
        serializer = VapiWebhookSerializer(
            data=webhook_data,
            context={'business': self.business}
        )
        serializer.is_valid(raise_exception=True)
        return serializer.save()
    
    def _process_event(self, event_type: str, call: VapiCall, webhook_data: Dict) -> Dict:
        if event_type == 'call.ended':
            return self._handle_call_ended(call)
        elif event_type == 'call.started':
            return self._handle_call_started(call)
        
        return {'action': 'logged'}
    
    def _handle_call_ended(self, call: VapiCall) -> Dict:
        if hasattr(call, 'analysis') and call.analysis.structured_data:
            from .tasks import process_call_completion
            process_call_completion.delay(call.id)
            return {'action': 'scheduled_processing'}
        
        return {'action': 'no_analysis_data'}
    
    def _handle_call_started(self, call: VapiCall) -> Dict:
        return {'action': 'call_started'}
