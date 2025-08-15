from rest_framework import permissions
from apps.core.viewsets import TenantViewSet
from apps.core.permissions import BusinessStaffPermission
from .models import Client
from apps.appointments.serializers import ClientSerializer


class ClientViewSet(TenantViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated, BusinessStaffPermission]
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    filterset_fields = ['email', 'phone']
    ordering = ['first_name', 'last_name']
