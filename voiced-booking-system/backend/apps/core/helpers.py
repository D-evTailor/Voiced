from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from .constants import STATUS_TRANSITIONS


def get_localized_day_name(day_of_week):
    from .choices import DAYS_OF_WEEK_CHOICES
    day_dict = dict(DAYS_OF_WEEK_CHOICES)
    return str(day_dict.get(day_of_week, _('Unknown')))


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


def parse_date_param(date_string, param_name="date"):
    if not date_string:
        return None
    
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError(f"Invalid {param_name} format. Use YYYY-MM-DD")


def parse_datetime_param(datetime_string, param_name="datetime"):
    if not datetime_string:
        return None
    
    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M']
    
    for fmt in formats:
        try:
            return datetime.strptime(datetime_string, fmt)
        except ValueError:
            continue
    
    raise ValidationError(f"Invalid {param_name} format")


def format_currency(amount, currency='EUR'):
    if amount is None:
        return ""
    
    currency_symbols = {
        'EUR': '€',
        'USD': '$',
        'GBP': '£',
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{amount:.2f} {symbol}"


def generate_time_slots(start_time, end_time, slot_duration=30):
    slots = []
    current = start_time
    
    while current < end_time:
        slots.append(current.strftime('%H:%M'))
        current += timedelta(minutes=slot_duration)
    
    return slots


def validate_business_context(request):
    if not hasattr(request, 'business') or not request.business:
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("Business context required")
    return request.business


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def format_time_range(start_time, end_time):
    if not start_time or not end_time:
        return ""
    return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"


def is_business_hours(dt, business_hours=None):
    if not business_hours:
        return True
    
    day_of_week = dt.weekday()
    hours = business_hours.filter(day_of_week=day_of_week, is_closed=False).first()
    
    if not hours or not hours.open_time or not hours.close_time:
        return False
    
    time_part = dt.time()
    return hours.open_time <= time_part <= hours.close_time
