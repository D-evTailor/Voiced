import factory
from django.contrib.auth import get_user_model
from django.db import transaction
from faker import Faker

User = get_user_model()
fake = Faker()


class BusinessHoursFactory:
    @staticmethod
    def create_default_hours(business):
        default_hours = []
        for day in range(7):
            if day < 5:
                default_hours.append({
                    'business': business,
                    'day_of_week': day,
                    'open_time': '09:00',
                    'close_time': '18:00'
                })
            else:
                default_hours.append({
                    'business': business,
                    'day_of_week': day,
                    'is_closed': True
                })
        return default_hours
    
    @staticmethod
    @transaction.atomic
    def create_business_hours(business, hours_data=None):
        from apps.businesses.models import BusinessHours
        
        if hours_data:
            for hour_data in hours_data:
                BusinessHours.objects.create(business=business, **hour_data)
        else:
            default_hours = BusinessHoursFactory.create_default_hours(business)
            for hour_data in default_hours:
                BusinessHours.objects.create(**hour_data)


class BusinessMemberFactory:
    @staticmethod
    def create_owner_membership(business):
        from apps.businesses.models import BusinessMember
        return BusinessMember.objects.create(
            business=business,
            user=business.owner,
            role='owner',
            is_primary=True
        )


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.LazyAttribute(lambda obj: fake.email())
    first_name = factory.LazyAttribute(lambda obj: fake.first_name())
    last_name = factory.LazyAttribute(lambda obj: fake.last_name())
    is_active = True
    is_verified = True
    locale = 'es'
    timezone = 'Europe/Madrid'


class BusinessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'businesses.Business'
    
    owner = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda obj: fake.company())
    slug = factory.LazyAttribute(lambda obj: fake.slug())
    email = factory.LazyAttribute(lambda obj: fake.company_email())
    phone = factory.LazyAttribute(lambda obj: fake.phone_number())
    address = factory.LazyAttribute(lambda obj: fake.address())
    city = factory.LazyAttribute(lambda obj: fake.city())
    state = factory.LazyAttribute(lambda obj: fake.state())
    postal_code = factory.LazyAttribute(lambda obj: fake.postcode())
    country = 'Spain'
    locale = 'es'
    timezone = 'Europe/Madrid'
    currency = 'EUR'
    is_active = True


class ServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'services.Service'
    
    business = factory.SubFactory(BusinessFactory)
    name = factory.LazyAttribute(lambda obj: fake.catch_phrase())
    description = factory.LazyAttribute(lambda obj: fake.text(max_nb_chars=200))
    duration = factory.LazyAttribute(lambda obj: fake.random_element(elements=[30, 45, 60, 90, 120]))
    price = factory.LazyAttribute(lambda obj: fake.pydecimal(left_digits=3, right_digits=2, positive=True))
    is_active = True
    online_booking_enabled = True
    voice_booking_enabled = True


class AppointmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'appointments.Appointment'
    
    business = factory.SubFactory(BusinessFactory)
    service = factory.SubFactory(ServiceFactory)
    customer_name = factory.LazyAttribute(lambda obj: fake.name())
    customer_email = factory.LazyAttribute(lambda obj: fake.email())
    customer_phone = factory.LazyAttribute(lambda obj: fake.phone_number())
    start_time = factory.LazyAttribute(lambda obj: fake.future_datetime())
    status = 'pending'
