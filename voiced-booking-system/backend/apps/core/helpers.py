from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from .constants import STATUS_TRANSITIONS


def get_display_name(obj, name_fields=None):
    if name_fields is None:
        name_fields = ['first_name', 'last_name', 'name', 'email', 'phone']
    
    parts = []
    for field in name_fields:
        if hasattr(obj, field):
            value = getattr(obj, field)
            if value:
                parts.append(str(value))
    
    if parts:
        return ' '.join(parts[:2])
    
    return f"{obj._meta.verbose_name} #{str(obj.id)[:8]}"


def format_duration(minutes):
    if not minutes:
        return None
    
    hours, mins = divmod(minutes, 60)
    if hours:
        return f"{hours}h {mins}m" if mins else f"{hours}h"
    return f"{mins}m"


def calculate_end_time(start_time, duration_minutes):
    if not start_time or not duration_minutes:
        return None
    return start_time + timedelta(minutes=duration_minutes)


def validate_status_transition(current_status, new_status, entity_type='appointment'):
    transitions = STATUS_TRANSITIONS.get(entity_type, {})
    allowed_statuses = transitions.get(current_status, [])
    
    if new_status not in allowed_statuses:
        raise ValidationError(
            _(f'Cannot change status from {current_status} to {new_status}')
        )


def get_business_hours_display(start_time, end_time, is_closed=False):
    if is_closed or not start_time or not end_time:
        return _('Closed')
    return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"


def truncate_text(text, max_length=50, suffix='...'):
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_decimal_add(*values):
    from decimal import Decimal, InvalidOperation
    result = Decimal('0')
    for value in values:
        try:
            if value:
                result += Decimal(str(value))
        except (InvalidOperation, TypeError):
            continue
    return result


def get_current_business_quarter():
    now = timezone.now()
    month = now.month
    year = now.year
    
    if month <= 3:
        return f"{year} Q1"
    elif month <= 6:
        return f"{year} Q2"
    elif month <= 9:
        return f"{year} Q3"
    else:
        return f"{year} Q4"


def normalize_phone_number(phone):
    if not phone:
        return phone
    
    import re
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    if cleaned.startswith('0'):
        cleaned = '+34' + cleaned[1:]
    elif not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    
    return cleaned
