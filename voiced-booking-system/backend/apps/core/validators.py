from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime, time
from .constants import APPOINTMENT_DURATION_LIMITS, BUSINESS_HOURS_LIMITS


def validate_time_range(start_time, end_time, field_name="time"):
    if start_time and end_time and start_time >= end_time:
        raise ValidationError(_(f'{field_name.title()} start must be before end'))


def validate_contact_info(email, phone):
    if not email and not phone:
        raise ValidationError(_('Either email or phone number is required'))


def validate_positive_number(value, field_name="value"):
    if value < 0:
        raise ValidationError(_(f'{field_name.title()} cannot be negative'))


def validate_range(value, min_val, max_val, field_name="value"):
    if value < min_val or value > max_val:
        raise ValidationError(
            _(f'{field_name.title()} must be between {min_val} and {max_val}')
        )


def validate_future_datetime(dt, field_name="datetime"):
    if dt < datetime.now():
        raise ValidationError(_(f'{field_name.title()} cannot be in the past'))


def validate_business_hours_time(dt):
    earliest = time(BUSINESS_HOURS_LIMITS['earliest'], 0)
    latest = time(BUSINESS_HOURS_LIMITS['latest'], 0)
    
    if dt.time() < earliest or dt.time() > latest:
        raise ValidationError(
            _(f'Time must be between {earliest.strftime("%H:%M")} and {latest.strftime("%H:%M")}')
        )


class BusinessValidators:
    @staticmethod
    def validate_business_hours(start_time, end_time):
        validate_time_range(start_time, end_time, "business hours")
    
    @staticmethod
    def validate_contact_info(email, phone):
        validate_contact_info(email, phone)


class AppointmentValidators:
    @staticmethod
    def validate_appointment_time(start_time, service_duration=None):
        validate_future_datetime(start_time, "appointment")
        validate_business_hours_time(start_time)


class ServiceValidators:
    @staticmethod
    def validate_duration(duration):
        validate_range(
            duration, 
            APPOINTMENT_DURATION_LIMITS['min'], 
            APPOINTMENT_DURATION_LIMITS['max'], 
            "service duration"
        )
    
    @staticmethod
    def validate_price(price):
        validate_positive_number(price, "price")
