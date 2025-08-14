import factory
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
fake = Faker()


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
    client_name = factory.LazyAttribute(lambda obj: fake.name())
    client_email = factory.LazyAttribute(lambda obj: fake.email())
    client_phone = factory.LazyAttribute(lambda obj: fake.phone_number())
    start_time = factory.LazyAttribute(lambda obj: fake.future_datetime())
    status = 'scheduled'
