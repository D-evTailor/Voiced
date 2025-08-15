from typing import Dict, List, Optional
import requests
from django.conf import settings
from django.core.cache import cache
from .optimizations import cached_method, circuit_breaker, VapiCacheKeys
import logging

logger = logging.getLogger(__name__)


class VapiAPIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.VAPI_API_KEY
        self.base_url = settings.VAPI_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
    
    @circuit_breaker
    def create_assistant(self, config: Dict) -> Dict:
        response = self.session.post(f'{self.base_url}/assistant', json=config)
        response.raise_for_status()
        return response.json()
    
    @circuit_breaker
    def update_assistant(self, assistant_id: str, config: Dict) -> Dict:
        response = self.session.patch(f'{self.base_url}/assistant/{assistant_id}', json=config)
        response.raise_for_status()
        return response.json()
    
    @circuit_breaker
    def get_assistant(self, assistant_id: str) -> Dict:
        response = self.session.get(f'{self.base_url}/assistant/{assistant_id}')
        response.raise_for_status()
        return response.json()
    
    @circuit_breaker
    def delete_assistant(self, assistant_id: str) -> bool:
        response = self.session.delete(f'{self.base_url}/assistant/{assistant_id}')
        response.raise_for_status()
        return True
    
    @circuit_breaker
    def create_phone_call(self, phone_number: str, assistant_id: str, **kwargs) -> Dict:
        payload = {
            'phoneNumberId': kwargs.get('phone_number_id'),
            'assistantId': assistant_id,
            'customer': {'number': phone_number},
            **kwargs
        }
        response = self.session.post(f'{self.base_url}/call/phone', json=payload)
        response.raise_for_status()
        return response.json()
    
    @circuit_breaker
    def get_call(self, call_id: str) -> Dict:
        response = self.session.get(f'{self.base_url}/call/{call_id}')
        response.raise_for_status()
        return response.json()
    
    @circuit_breaker
    def list_calls(self, limit: int = 100, **filters) -> Dict:
        params = {'limit': limit, **filters}
        response = self.session.get(f'{self.base_url}/call', params=params)
        response.raise_for_status()
        return response.json()
    
    @circuit_breaker
    def buy_phone_number(self, area_code: str = None, name: str = None) -> Dict:
        payload = {}
        if area_code:
            payload['areaCode'] = area_code
        if name:
            payload['name'] = name
        
        response = self.session.post(f'{self.base_url}/phone-number/buy', json=payload)
        response.raise_for_status()
        return response.json()
    
    @circuit_breaker
    def list_phone_numbers(self) -> List[Dict]:
        response = self.session.get(f'{self.base_url}/phone-number')
        response.raise_for_status()
        return response.json()
    
    @circuit_breaker
    def update_phone_number(self, phone_number_id: str, config: Dict) -> Dict:
        response = self.session.patch(f'{self.base_url}/phone-number/{phone_number_id}', json=config)
        response.raise_for_status()
        return response.json()


class VapiBusinessService:
    def __init__(self, business):
        self.business = business
        self.client = VapiAPIClient()
    
    @cached_method(timeout=3600, key_func=lambda self: VapiCacheKeys.assistant(self.business.id))
    def get_or_create_assistant(self) -> str:
        config = self.business.vapi_configurations.filter(is_active=True).first()
        if not config:
            raise ValueError("No active VAPI configuration found")
        
        if config.assistant_id:
            try:
                self.client.get_assistant(config.assistant_id)
                return config.assistant_id
            except requests.HTTPError:
                pass
        
        assistant_config = self._build_assistant_config(config)
        result = self.client.create_assistant(assistant_config)
        
        config.assistant_id = result['id']
        config.save()
        
        logger.info(f"Created assistant {result['id']} for business {self.business.id}")
        return result['id']
    
    def _build_assistant_config(self, config) -> Dict:
        return {
            **config.assistant_config,
            'tools': self._get_business_tools(),
            'name': config.assistant_name,
            'serverUrl': config.server_url,
            'serverUrlSecret': config.server_secret,
        }
    
    def _get_business_tools(self) -> List[Dict]:
        return [
            {
                'type': 'function',
                'function': {
                    'name': 'get_available_services',
                    'description': f'Get available services for {self.business.name}',
                    'parameters': {
                        'type': 'object',
                        'properties': {},
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'check_availability',
                    'description': 'Check availability for a specific service and date',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'service_id': {'type': 'integer', 'description': 'Service ID'},
                            'date': {'type': 'string', 'description': 'Date in ISO format'},
                            'duration': {'type': 'integer', 'description': 'Duration in minutes'}
                        },
                        'required': ['service_id', 'date']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'book_appointment',
                    'description': 'Book an appointment',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'service_id': {'type': 'integer'},
                            'datetime': {'type': 'string', 'description': 'Appointment datetime in ISO format'},
                            'client_name': {'type': 'string'},
                            'client_phone': {'type': 'string'},
                            'client_email': {'type': 'string'},
                            'notes': {'type': 'string'}
                        },
                        'required': ['service_id', 'datetime', 'client_name', 'client_phone']
                    }
                }
            }
        ]
    
    def make_outbound_call(self, phone_number: str, **kwargs) -> Dict:
        assistant_id = self.get_or_create_assistant()
        config = self.business.vapi_configurations.filter(is_active=True).first()
        
        return self.client.create_phone_call(
            phone_number=phone_number,
            assistant_id=assistant_id,
            phone_number_id=config.phone_number_id,
            **kwargs
        )
