from django.core.management.base import BaseCommand
from apps.vapi_integration.multi_tenant_services import TenantRegistrationService, SharedAgentManager
from apps.businesses.models import Business


class Command(BaseCommand):
    help = 'Initialize VAPI shared agent and setup multi-tenant infrastructure'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['init-shared-agent', 'register-existing-businesses', 'status'],
            help='Action to perform'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'init-shared-agent':
            self.init_shared_agent()
        elif action == 'register-existing-businesses':
            self.register_existing_businesses()
        elif action == 'status':
            self.show_status()

    def init_shared_agent(self):
        try:
            shared_agent = SharedAgentManager()
            agent_id = shared_agent.shared_agent_id
            self.stdout.write(
                self.style.SUCCESS(f'Shared agent initialized: {agent_id}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to initialize shared agent: {e}')
            )

    def register_existing_businesses(self):
        businesses = Business.objects.filter(
            is_active=True,
            vapi_configurations__isnull=True
        )
        
        service = TenantRegistrationService()
        registered_count = 0
        
        for business in businesses:
            try:
                result = service.register_tenant(business)
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f'Registered: {business.name}')
                    )
                    registered_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to register {business.name}: {result.get("error")}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error registering {business.name}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully registered {registered_count} businesses')
        )

    def show_status(self):
        try:
            shared_agent = SharedAgentManager()
            agent_id = shared_agent.shared_agent_id
            self.stdout.write(f'Shared Agent ID: {agent_id}')
            
            total_businesses = Business.objects.filter(is_active=True).count()
            configured_businesses = Business.objects.filter(
                is_active=True,
                vapi_configurations__is_active=True
            ).count()
            
            self.stdout.write(f'Total businesses: {total_businesses}')
            self.stdout.write(f'VAPI configured: {configured_businesses}')
            self.stdout.write(f'Pending configuration: {total_businesses - configured_businesses}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to get status: {e}')
            )
