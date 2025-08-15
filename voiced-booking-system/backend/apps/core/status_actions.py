from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from .exceptions import success_response


class StatusActionsMixin:
    def confirm_action(self, request, pk=None):
        instance = self.get_object()
        instance.status = 'confirmed'
        instance.save(update_fields=['status'])
        return {'status': instance.status, 'message': f"{instance._meta.verbose_name} confirmed"}
    
    def cancel_action(self, request, pk=None):
        instance = self.get_object()
        instance.status = 'cancelled'
        reason = request.data.get('reason', '')
        update_fields = ['status']
        
        if hasattr(instance, 'cancellation_reason'):
            instance.cancellation_reason = reason
            update_fields.append('cancellation_reason')
        
        instance.save(update_fields=update_fields)
        return {'status': instance.status, 'message': f"{instance._meta.verbose_name} cancelled"}
    
    def complete_action(self, request, pk=None):
        instance = self.get_object()
        instance.status = 'completed'
        update_fields = ['status']
        
        if hasattr(instance, 'completed_at'):
            from django.utils import timezone
            instance.completed_at = timezone.now()
            update_fields.append('completed_at')
        
        instance.save(update_fields=update_fields)
        return {'status': instance.status, 'message': f"{instance._meta.verbose_name} completed"}
    
    def toggle_active_action(self, request, pk=None):
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save(update_fields=['is_active'])
        status_text = 'activated' if instance.is_active else 'deactivated'
        return {'is_active': instance.is_active, 'message': f"{instance._meta.verbose_name} {status_text}"}


class FilterActionsMixin:
    def get_today_queryset(self, request):
        from django.utils import timezone
        today = timezone.now().date()
        field_name = getattr(self, 'date_field', 'created_at')
        filter_kwargs = {f'{field_name}__date': today}
        return self.get_queryset().filter(**filter_kwargs)
    
    def get_upcoming_queryset(self, request):
        from django.utils import timezone
        now = timezone.now()
        field_name = getattr(self, 'date_field', 'created_at')
        status_field = getattr(self, 'status_field', 'status')
        valid_statuses = getattr(self, 'upcoming_statuses', ['pending', 'confirmed'])
        
        filter_kwargs = {
            f'{field_name}__gte': now,
            f'{status_field}__in': valid_statuses
        }
        return self.get_queryset().filter(**filter_kwargs)[:10]
    
    def get_active_queryset(self, request):
        return self.get_queryset().filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        queryset = self.get_today_queryset(request)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        queryset = self.get_upcoming_queryset(request)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)
