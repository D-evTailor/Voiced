from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.businesses.models import Business, BusinessMember

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with a business'
    
    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Superuser email')
        parser.add_argument('--password', required=True, help='Superuser password')
        parser.add_argument('--business', required=True, help='Business name')
    
    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        business_name = options['business']
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'User with email {email} already exists')
            )
            return
        
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name='Super',
            last_name='Admin'
        )
        
        business = Business.objects.create(
            owner=user,
            name=business_name,
            slug=business_name.lower().replace(' ', '-'),
            email=email,
            phone='+34600000000',
            address='Admin Address 123',
            city='Madrid',
            state='Madrid',
            postal_code='28001',
            country='Spain'
        )
        
        BusinessMember.objects.create(
            business=business,
            user=user,
            role='owner',
            is_primary=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created superuser {email} with business {business_name}'
            )
        )
