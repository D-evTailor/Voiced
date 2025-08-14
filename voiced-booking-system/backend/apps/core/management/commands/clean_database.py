from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection


class Command(BaseCommand):
    help = 'Clean database by removing all data from tenant-specific tables'
    
    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', help='Confirm the action')
    
    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING('This will delete all data from tenant tables. Use --confirm to proceed.')
            )
            return
        
        tenant_models = [
            'appointments.Appointment',
            'appointments.Client', 
            'services.ServiceProvider',
            'services.Service',
            'services.ServiceCategory',
            'businesses.BusinessMember',
            'businesses.BusinessHours',
            'businesses.Business',
            'payments.Payment',
            'payments.Subscription',
            'vapi_integration.VapiCallLog',
            'vapi_integration.VapiConfiguration',
            'notifications.Notification',
            'analytics.BusinessMetrics',
            'analytics.AuditLog',
            'resources.ResourceBlock',
            'resources.ResourceSchedule',
            'resources.AppointmentResource',
            'resources.ServiceResource',
            'resources.Resource',
        ]
        
        with connection.cursor() as cursor:
            cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
            
            for model_path in tenant_models:
                try:
                    model = apps.get_model(model_path)
                    count = model.objects.count()
                    model.objects.all().delete()
                    self.stdout.write(f'Deleted {count} records from {model._meta.db_table}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error deleting from {model_path}: {e}')
                    )
            
            cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')
        
        self.stdout.write(self.style.SUCCESS('Database cleaned successfully!'))
