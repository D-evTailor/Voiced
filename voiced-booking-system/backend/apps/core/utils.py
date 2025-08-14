from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


PHONE_REGEX_VALIDATOR = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message=_('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
)

COMMON_STATUS_CHOICES = [
    ('active', _('Active')),
    ('inactive', _('Inactive')),
    ('pending', _('Pending')),
    ('cancelled', _('Cancelled')),
]

LANGUAGE_CHOICES = [
    ('es', _('Spanish')),
    ('en', _('English')),
]

CURRENCY_CHOICES = [
    ('EUR', _('Euro')),
    ('USD', _('US Dollar')),
    ('GBP', _('British Pound')),
]

BUSINESS_TYPE_CHOICES = [
    ('salon', _('Hair Salon')),
    ('clinic', _('Medical Clinic')),
    ('restaurant', _('Restaurant')),
    ('spa', _('Spa')),
    ('dental', _('Dental Clinic')),
    ('veterinary', _('Veterinary')),
    ('fitness', _('Fitness Center')),
    ('other', _('Other'))
]

APPOINTMENT_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('confirmed', _('Confirmed')),
    ('in_progress', _('In Progress')),
    ('completed', _('Completed')),
    ('cancelled', _('Cancelled')),
    ('no_show', _('No Show')),
    ('rescheduled', _('Rescheduled')),
]

APPOINTMENT_SOURCE_CHOICES = [
    ('online', _('Online Booking')),
    ('voice_agent', _('Voice Agent')),
    ('manual', _('Manual Entry')),
    ('phone_call', _('Phone Call')),
    ('walk_in', _('Walk In')),
    ('mobile_app', _('Mobile App')),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('paid', _('Paid')),
    ('partially_paid', _('Partially Paid')),
    ('refunded', _('Refunded')),
    ('failed', _('Failed')),
    ('waived', _('Waived')),
]

RESOURCE_TYPE_CHOICES = [
    ('staff', _('Staff')),
    ('room', _('Room')),
    ('equipment', _('Equipment')),
]

COUNTRY_CHOICES = [
    ('ES', _('Spain')),
    ('US', _('United States')),
    ('GB', _('United Kingdom')),
    ('FR', _('France')),
    ('DE', _('Germany')),
]


def generate_unique_reference(prefix, date_obj, length=5):
    import random
    import string
    
    date_part = date_obj.strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    return f"{prefix}-{date_part}-{random_part}"


def calculate_percentage_change(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100


def get_business_hours_display(start_time, end_time, is_closed=False):
    if is_closed or not start_time or not end_time:
        return _('Closed')
    return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"


def get_vapi_context_for_business_type(business_type):
    contexts = {
        'salon': 'Hair salon specializing in cuts, color, and styling services.',
        'clinic': 'Medical clinic providing healthcare and consultation services.',
        'restaurant': 'Restaurant offering dining reservations and table booking.',
        'spa': 'Spa offering wellness and beauty treatments.',
        'dental': 'Dental clinic providing oral health and dental care services.',
        'veterinary': 'Veterinary clinic providing animal health services.',
        'fitness': 'Fitness center offering training and workout sessions.',
    }
    return contexts.get(business_type, 'Business offering appointment-based services.')
