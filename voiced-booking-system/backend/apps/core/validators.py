from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime, time


class BusinessValidators:
    @staticmethod
    def validate_business_hours(start_time, end_time):
        if start_time and end_time and start_time >= end_time:
            raise ValidationError(_('Start time must be before end time'))
    
    @staticmethod
    def validate_contact_info(email, phone):
        if not email and not phone:
            raise ValidationError(_('Either email or phone number is required'))


class AppointmentValidators:
    @staticmethod
    def validate_appointment_time(start_time, service_duration):
        if start_time < datetime.now():
            raise ValidationError(_('Appointment cannot be in the past'))
        
        if start_time.time() < time(6, 0) or start_time.time() > time(23, 0):
            raise ValidationError(_('Appointments must be between 6:00 AM and 11:00 PM'))


class ServiceValidators:
    @staticmethod
    def validate_duration(duration):
        if duration < 5:
            raise ValidationError(_('Service duration must be at least 5 minutes'))
        if duration > 480:
            raise ValidationError(_('Service duration cannot exceed 8 hours'))
    
    @staticmethod
    def validate_price(price):
        if price < 0:
            raise ValidationError(_('Price cannot be negative'))
