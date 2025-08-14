from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Client


@receiver([post_save, post_delete], sender='appointments.Appointment')
def update_client_statistics(sender, instance, **kwargs):
    if hasattr(instance, 'client') and instance.client:
        instance.client.update_statistics()
