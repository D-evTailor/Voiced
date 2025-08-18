from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import TenantPermission
from .models import Notification, NotificationTemplate
from .serializers import NotificationSerializer, NotificationTemplateSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, TenantPermission]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user, business=self.request.business)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, TenantPermission]
    serializer_class = NotificationTemplateSerializer
    
    def get_queryset(self):
        return NotificationTemplate.objects.filter(business=self.request.business)
