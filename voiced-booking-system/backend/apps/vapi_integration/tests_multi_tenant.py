"""
Multi-tenant VAPI Integration Tests
"""
import json
from unittest.mock import patch, Mock
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from apps.businesses.models import Business
from apps.vapi_integration.models import VapiConfiguration
from apps.vapi_integration.multi_tenant_services import (
    SharedAgentManager, 
    TenantRegistrationService, 
    MetadataExtractor
)

User = get_user_model()


class SharedAgentManagerTests(TestCase):
    @patch('apps.vapi_integration.multi_tenant_services.VapiService')
    def setUp(self, mock_vapi_service):
        self.mock_vapi = mock_vapi_service.return_value
        self.shared_agent_manager = SharedAgentManager()

    def test_get_or_create_shared_agent(self):
        self.mock_vapi.get_assistant.return_value = {
            'id': 'shared-agent-123',
            'name': 'Multi-Tenant Assistant'
        }
        
        agent_id = self.shared_agent_manager.shared_agent_id
        self.assertEqual(agent_id, 'shared-agent-123')

    @patch('apps.vapi_integration.multi_tenant_services.VapiService')
    def test_create_new_shared_agent(self, mock_vapi_service):
        mock_vapi = mock_vapi_service.return_value
        mock_vapi.get_assistant.side_effect = Exception("Not found")
        mock_vapi.create_assistant.return_value = {
            'id': 'new-shared-agent-456',
            'name': 'Multi-Tenant Assistant'
        }
        
        manager = SharedAgentManager()
        agent_id = manager.shared_agent_id
        self.assertEqual(agent_id, 'new-shared-agent-456')


class TenantRegistrationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.business = Business.objects.create(
            name='Test Business',
            slug='test-business',
            owner=self.user,
            email='business@test.com',
            phone='+1234567890'
        )

    @patch('apps.vapi_integration.multi_tenant_services.SharedAgentManager')
    @patch('apps.vapi_integration.multi_tenant_services.VapiService')
    def test_register_tenant_success(self, mock_vapi_service, mock_shared_agent):
        # Setup mocks
        mock_shared_agent.return_value.shared_agent_id = 'shared-agent-123'
        mock_vapi = mock_vapi_service.return_value
        mock_vapi.buy_phone_number.return_value = {
            'phoneNumber': '+1987654321',
            'id': 'phone-number-id'
        }
        mock_vapi.create_phone_number.return_value = {
            'id': 'vapi-phone-id',
            'number': '+1987654321'
        }

        service = TenantRegistrationService()
        result = service.register_tenant(self.business)

        self.assertTrue(result['success'])
        self.assertIn('configuration', result)
        
        # Verify configuration was created
        config = VapiConfiguration.objects.get(business=self.business)
        self.assertEqual(config.vapi_assistant_id, 'shared-agent-123')
        self.assertTrue(config.is_shared_agent)

    @patch('apps.vapi_integration.multi_tenant_services.SharedAgentManager')
    @patch('apps.vapi_integration.multi_tenant_services.VapiService')
    def test_register_tenant_phone_purchase_failure(self, mock_vapi_service, mock_shared_agent):
        mock_shared_agent.return_value.shared_agent_id = 'shared-agent-123'
        mock_vapi = mock_vapi_service.return_value
        mock_vapi.buy_phone_number.side_effect = Exception("Failed to buy phone")

        service = TenantRegistrationService()
        result = service.register_tenant(self.business)

        self.assertFalse(result['success'])
        self.assertIn('error', result)


class MetadataExtractorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.business = Business.objects.create(
            name='Test Business',
            slug='test-business',
            owner=self.user,
            email='business@test.com',
            phone='+1234567890'
        )

    def test_extract_from_webhook_with_call_data(self):
        webhook_data = {
            'type': 'call.started',
            'call': {
                'metadata': {
                    'business_id': str(self.business.id),
                    'business_slug': 'test-business'
                }
            }
        }

        extractor = MetadataExtractor()
        result = extractor.extract_tenant_info(webhook_data)

        self.assertEqual(result['business_id'], str(self.business.id))
        self.assertEqual(result['business_slug'], 'test-business')

    def test_extract_from_webhook_with_message_data(self):
        webhook_data = {
            'type': 'message.received',
            'message': {
                'call': {
                    'metadata': {
                        'business_id': str(self.business.id)
                    }
                }
            }
        }

        extractor = MetadataExtractor()
        result = extractor.extract_tenant_info(webhook_data)

        self.assertEqual(result['business_id'], str(self.business.id))

    def test_get_business_from_metadata(self):
        metadata = {
            'business_id': str(self.business.id),
            'business_slug': 'test-business'
        }

        extractor = MetadataExtractor()
        business = extractor.get_business_from_metadata(metadata)

        self.assertEqual(business, self.business)

    def test_get_business_from_metadata_not_found(self):
        metadata = {
            'business_id': '999999',
            'business_slug': 'non-existent'
        }

        extractor = MetadataExtractor()
        business = extractor.get_business_from_metadata(metadata)

        self.assertIsNone(business)


class WebhookProcessingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.business = Business.objects.create(
            name='Test Business',
            slug='test-business',
            owner=self.user,
            email='business@test.com',
            phone='+1234567890'
        )
        self.config = VapiConfiguration.objects.create(
            business=self.business,
            vapi_assistant_id='shared-agent-123',
            is_shared_agent=True,
            is_active=True
        )

    @patch('apps.vapi_integration.processors.WebhookProcessor.process_webhook')
    def test_webhook_with_tenant_metadata(self, mock_process):
        webhook_data = {
            'type': 'call.started',
            'call': {
                'id': 'call-123',
                'metadata': {
                    'business_id': str(self.business.id),
                    'business_slug': 'test-business'
                }
            }
        }

        # This would be called by the webhook view
        from apps.vapi_integration.processors import WebhookProcessor
        processor = WebhookProcessor()
        processor.process_webhook(webhook_data)

        mock_process.assert_called_once_with(webhook_data)


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True
)
class AsyncTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.business = Business.objects.create(
            name='Test Business',
            slug='test-business',
            owner=self.user,
            email='business@test.com',
            phone='+1234567890'
        )

    @patch('apps.vapi_integration.multi_tenant_services.TenantRegistrationService')
    def test_register_tenant_async_task(self, mock_service):
        mock_service.return_value.register_tenant.return_value = {
            'success': True,
            'configuration': {'id': 'config-123'}
        }

        from apps.vapi_integration.tasks import register_tenant_async
        result = register_tenant_async.apply(args=[self.business.id])

        self.assertTrue(result.successful())
        mock_service.return_value.register_tenant.assert_called_once()
