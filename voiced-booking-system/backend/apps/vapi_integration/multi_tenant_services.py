from typing import Dict, Optional
from django.db import transaction
from django.conf import settings
from apps.businesses.models import Business
from .api_client import VapiAPIClient
from .models import VapiConfiguration
from .optimizations import cache_service, VapiCacheKeys
import logging

logger = logging.getLogger(__name__)


class SharedAgentManager:
    def __init__(self):
        self.client = VapiAPIClient()
        self._shared_agent_id = None
    
    @property
    def shared_agent_id(self) -> str:
        if not self._shared_agent_id:
            self._shared_agent_id = self._get_or_create_shared_agent()
        return self._shared_agent_id
    
    def _get_or_create_shared_agent(self) -> str:
        shared_agent_id = getattr(settings, 'VAPI_SHARED_AGENT_ID', None)
        
        if shared_agent_id:
            try:
                self.client.get_assistant(shared_agent_id)
                return shared_agent_id
            except Exception:
                pass
        
        assistant_config = self._build_shared_agent_config()
        result = self.client.create_assistant(assistant_config)
        
        logger.info(f"Created shared agent: {result['id']}")
        return result['id']
    
    def _build_shared_agent_config(self) -> Dict:
        return {
            'name': 'Multi-Tenant Booking Assistant',
            'firstMessage': 'Hola, bienvenido a nuestro sistema de reservas. ¿En qué puedo ayudarte hoy?',
            'voice': {'provider': 'openai', 'voiceId': 'nova'},
            'model': {'provider': 'openai', 'model': 'gpt-4o-mini'},
            'serverUrl': f"{settings.VAPI_WEBHOOK_BASE_URL}/vapi/webhook/",
            'tools': self._get_shared_tools(),
            'systemMessage': self._get_shared_system_message(),
        }
    
    def _get_shared_tools(self) -> list:
        return [
            {
                'type': 'function',
                'function': {
                    'name': 'get_business_services',
                    'description': 'Get available services for a business',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'business_name': {'type': 'string', 'description': 'Name of the business'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'check_availability',
                    'description': 'Check availability for a service',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'service_name': {'type': 'string'},
                            'date': {'type': 'string', 'description': 'Date in YYYY-MM-DD format'},
                            'time_preference': {'type': 'string', 'description': 'Preferred time'}
                        },
                        'required': ['service_name', 'date']
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
                            'service_name': {'type': 'string'},
                            'datetime': {'type': 'string', 'description': 'Appointment datetime in ISO format'},
                            'client_name': {'type': 'string'},
                            'client_phone': {'type': 'string'},
                            'client_email': {'type': 'string'},
                            'notes': {'type': 'string'}
                        },
                        'required': ['service_name', 'datetime', 'client_name', 'client_phone']
                    }
                }
            }
        ]
    
    def _get_shared_system_message(self) -> str:
        return """Eres un asistente de reservas para múltiples negocios. 
Tu objetivo es ayudar a los clientes a reservar citas de manera eficiente.
Siempre sé cortés y profesional. Si necesitas información específica del negocio, 
usa las herramientas disponibles. Confirma todos los detalles antes de hacer una reserva."""


class TenantRegistrationService:
    def __init__(self):
        self.client = VapiAPIClient()
        self.shared_agent = SharedAgentManager()
    
    @transaction.atomic
    def register_tenant(self, business: Business, area_code: Optional[str] = None) -> Dict:
        try:
            phone_result = self._provision_phone_number(business, area_code)
            config_result = self._create_vapi_configuration(business, phone_result)
            
            logger.info(f"Tenant registered successfully: {business.name}")
            return {
                'success': True,
                'business_id': business.id,
                'phone_number': phone_result['number'],
                'phone_number_id': phone_result['id']
            }
        except Exception as e:
            logger.error(f"Tenant registration failed for {business.name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _provision_phone_number(self, business: Business, area_code: Optional[str]) -> Dict:
        phone_result = self.client.buy_phone_number(
            area_code=area_code,
            name=f"{business.name} - {business.slug}"
        )
        
        metadata = {'tenant_id': str(business.id), 'business_slug': business.slug}
        
        self.client.update_phone_number(phone_result['id'], {
            'assistantId': self.shared_agent.shared_agent_id,
            'metadata': metadata
        })
        
        return phone_result
    
    def _create_vapi_configuration(self, business: Business, phone_result: Dict) -> VapiConfiguration:
        return VapiConfiguration.objects.create(
            business=business,
            phone_number_id=phone_result['id'],
            assistant_id=self.shared_agent.shared_agent_id,
            assistant_name='Shared Multi-Tenant Assistant',
            server_url=f"{settings.VAPI_WEBHOOK_BASE_URL}/vapi/webhook/",
            server_secret=settings.VAPI_WEBHOOK_SECRET,
            is_shared_agent=True
        )


class MetadataExtractor:
    @staticmethod
    def extract_tenant_info(webhook_data: Dict) -> Optional[Dict]:
        call_data = webhook_data.get('message', {}).get('call', {})
        
        metadata = call_data.get('metadata', {})
        if metadata and 'tenant_id' in metadata:
            return {
                'tenant_id': metadata['tenant_id'],
                'business_slug': metadata.get('business_slug', '')
            }
        
        phone_number_data = call_data.get('phoneNumber', {})
        if phone_number_data and 'metadata' in phone_number_data:
            metadata = phone_number_data['metadata']
            if 'tenant_id' in metadata:
                return {
                    'tenant_id': metadata['tenant_id'],
                    'business_slug': metadata.get('business_slug', '')
                }
        
        return None
    
    @staticmethod
    def get_business_from_metadata(webhook_data: Dict) -> Optional[Business]:
        tenant_info = MetadataExtractor.extract_tenant_info(webhook_data)
        if not tenant_info:
            return None
        
        try:
            return Business.objects.get(id=tenant_info['tenant_id'])
        except (Business.DoesNotExist, ValueError):
            return None
