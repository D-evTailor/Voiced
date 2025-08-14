from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.businesses.models import Business, BusinessMember
from apps.services.models import Service, ServiceCategory
from apps.appointments.models import Client, Appointment
from apps.core.factories import UserFactory, BusinessFactory, ServiceFactory
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for development'
    
    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of users to create')
        parser.add_argument('--businesses', type=int, default=3, help='Number of businesses to create')
        parser.add_argument('--services', type=int, default=10, help='Number of services to create')
        parser.add_argument('--appointments', type=int, default=20, help='Number of appointments to create')
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        users = []
        for i in range(options['users']):
            user = UserFactory()
            users.append(user)
            self.stdout.write(f'Created user: {user.email}')
        
        businesses = []
        for i in range(options['businesses']):
            business = BusinessFactory(owner=users[i % len(users)])
            businesses.append(business)
            self.stdout.write(f'Created business: {business.name}')
        
        categories = []
        for business in businesses:
            category = ServiceCategory.objects.create(
                business=business,
                name='General Services',
                description='General business services',
                created_by=business.owner
            )
            categories.append(category)
        
        services = []
        for i in range(options['services']):
            business = businesses[i % len(businesses)]
            category = categories[businesses.index(business)]
            
            service = ServiceFactory(
                business=business,
                category=category,
                created_by=business.owner
            )
            services.append(service)
            self.stdout.write(f'Created service: {service.name}')
        
        clients = []
        for business in businesses:
            for i in range(5):
                client = Client.objects.create(
                    business=business,
                    first_name=f'Client{i}',
                    last_name=f'Test{business.id}',
                    email=f'client{i}@{business.slug}.com',
                    phone=f'+34{600000000 + i}',
                    created_by=business.owner
                )
                clients.append(client)
        
        for i in range(options['appointments']):
            service = services[i % len(services)]
            business_clients = [c for c in clients if c.business == service.business]
            
            if business_clients:
                client = business_clients[i % len(business_clients)]
                start_time = timezone.now() + timedelta(days=i % 30, hours=9 + (i % 8))
                
                appointment = Appointment.objects.create(
                    business=service.business,
                    service=service,
                    client=client,
                    start_time=start_time,
                    status='scheduled',
                    created_by=service.business.owner
                )
                self.stdout.write(f'Created appointment: {appointment.id}')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
