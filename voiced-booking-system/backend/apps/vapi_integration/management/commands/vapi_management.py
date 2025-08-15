from django.core.management.base import BaseCommand
from django.conf import settings
from apps.businesses.models import Business
from apps.vapi_integration.api_client import VapiBusinessService, VapiAPIClient
from apps.vapi_integration.models import VapiConfiguration
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Manage VAPI integration operations'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['sync-assistants', 'create-assistant', 'list-phone-numbers', 'buy-phone-number'],
            help='Action to perform'
        )
        parser.add_argument('--business-id', type=int, help='Business ID for specific operations')
        parser.add_argument('--business-slug', type=str, help='Business slug for specific operations')
        parser.add_argument('--area-code', type=str, help='Area code for buying phone number')
        parser.add_argument('--phone-name', type=str, help='Name for the phone number')

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'sync-assistants':
            self.sync_assistants(options)
        elif action == 'create-assistant':
            self.create_assistant(options)
        elif action == 'list-phone-numbers':
            self.list_phone_numbers()
        elif action == 'buy-phone-number':
            self.buy_phone_number(options)

    def sync_assistants(self, options):
        businesses = self._get_businesses(options)
        synced_count = 0
        
        for business in businesses:
            try:
                service = VapiBusinessService(business)
                assistant_id = service.get_or_create_assistant()
                self.stdout.write(
                    self.style.SUCCESS(f'Synced assistant {assistant_id} for {business.name}')
                )
                synced_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to sync assistant for {business.name}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully synced {synced_count} assistants')
        )

    def create_assistant(self, options):
        businesses = self._get_businesses(options)
        
        for business in businesses:
            try:
                service = VapiBusinessService(business)
                assistant_id = service.get_or_create_assistant()
                self.stdout.write(
                    self.style.SUCCESS(f'Created assistant {assistant_id} for {business.name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create assistant for {business.name}: {e}')
                )

    def list_phone_numbers(self):
        try:
            client = VapiAPIClient()
            phone_numbers = client.list_phone_numbers()
            
            self.stdout.write(self.style.SUCCESS('Available phone numbers:'))
            for phone in phone_numbers:
                self.stdout.write(f"  {phone.get('number')} - {phone.get('name', 'Unnamed')}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to list phone numbers: {e}'))

    def buy_phone_number(self, options):
        try:
            client = VapiAPIClient()
            result = client.buy_phone_number(
                area_code=options.get('area_code'),
                name=options.get('phone_name')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Bought phone number: {result.get("number")}')
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to buy phone number: {e}'))

    def _get_businesses(self, options):
        if options.get('business_id'):
            return Business.objects.filter(id=options['business_id'])
        elif options.get('business_slug'):
            return Business.objects.filter(slug=options['business_slug'])
        else:
            return Business.objects.filter(is_active=True)
