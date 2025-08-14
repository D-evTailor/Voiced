import uuid
import random
import string
from datetime import datetime
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


PHONE_REGEX_VALIDATOR = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message=_('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
)

BUSINESS_TYPE_CHOICES = [
    ('salon', _('Hair Salon')),
    ('clinic', _('Medical Clinic')),
    ('restaurant', _('Restaurant')),
    ('spa', _('Spa')),
    ('dental', _('Dental Clinic')),
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
]

APPOINTMENT_SOURCE_CHOICES = [
    ('online', _('Online')),
    ('phone', _('Phone')),
    ('walk_in', _('Walk-in')),
    ('vapi', _('Voice AI')),
    ('admin', _('Admin')),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('paid', _('Paid')),
    ('partial', _('Partial')),
    ('failed', _('Failed')),
    ('refunded', _('Refunded')),
]

CLIENT_SOURCE_CHOICES = [
    ('website', _('Website')),
    ('referral', _('Referral')),
    ('social_media', _('Social Media')),
    ('vapi', _('Voice AI')),
    ('walk_in', _('Walk-in')),
    ('admin', _('Admin')),
]

RESOURCE_TYPE_CHOICES = [
    ('staff', _('Staff')),
    ('room', _('Room')),
    ('equipment', _('Equipment')),
]


def generate_unique_id():
    return str(uuid.uuid4())


def generate_unique_reference(prefix, date_obj, length=6):
    if isinstance(date_obj, datetime):
        date_str = date_obj.strftime('%y%m%d')
    else:
        date_str = date_obj.strftime('%y%m%d')
    
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}{date_str}{random_part}"


def generate_slug(text, max_length=50):
    return slugify(text)[:max_length]


def calculate_percentage_change(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100


def get_business_hours_display(start_time, end_time, is_closed=False):
    if is_closed or not start_time or not end_time:
        return _('Closed')
    return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
