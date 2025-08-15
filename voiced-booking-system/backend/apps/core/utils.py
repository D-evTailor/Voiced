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

def generate_unique_reference(prefix, date_obj, length=6):
    date_str = date_obj.strftime('%y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}{date_str}{random_part}"

def generate_slug(text, max_length=50):
    return slugify(text)[:max_length]

def calculate_percentage_change(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100
