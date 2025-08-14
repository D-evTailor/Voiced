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
