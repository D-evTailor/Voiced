import random
import string
from datetime import datetime
from typing import Optional
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

PHONE_REGEX_VALIDATOR = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message=_('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
)

RESOURCE_TYPE_CHOICES = [
    ('staff', _('Staff')),
    ('room', _('Room')),
    ('equipment', _('Equipment')),
]


def generate_unique_reference(prefix, date_obj=None, length=6):
    if date_obj is None:
        date_obj = datetime.now()
    date_str = date_obj.strftime('%y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}{date_str}{random_part}"


def generate_slug(text, max_length=50):
    return slugify(text)[:max_length]


def calculate_percentage_change(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100


def generate_api_key(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def mask_sensitive_data(data, fields=None):
    if fields is None:
        fields = ['password', 'api_key', 'secret', 'token']
    
    if isinstance(data, dict):
        return {
            key: '***' if any(field in key.lower() for field in fields) else value
            for key, value in data.items()
        }
    return data


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_model_fields(model, exclude_fields=None):
    if exclude_fields is None:
        exclude_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    return [field.name for field in model._meta.fields if field.name not in exclude_fields]


def clean_dict(d):
    return {k: v for k, v in d.items() if v is not None and v != ''}


def get_nested_value(obj, path, default=None):
    keys = path.split('.')
    current = obj
    
    try:
        for key in keys:
            if hasattr(current, key):
                current = getattr(current, key)
            elif isinstance(current, dict):
                current = current[key]
            else:
                return default
        return current
    except (KeyError, AttributeError, TypeError):
        return default


def extract_business_slug_from_path(path: str) -> Optional[str]:
    import re
    pattern = r'/dashboard/([^/]+)/?'
    match = re.search(pattern, path)
    return match.group(1) if match else None
