from rest_framework import permissions
from rest_framework.decorators import action
from apps.core.viewsets import TenantViewSet
from apps.core.permissions import BusinessManagerPermission, BusinessStaffPermission
from apps.core.exceptions import success_response, error_response
from .models import Service, ServiceCategory, ServiceProvider
from .serializers import (
    ServiceSerializer, ServiceCreateSerializer, ServiceUpdateSerializer,
    ServiceListSerializer, ServiceCategorySerializer, ServiceProviderSerializer
)


class ServiceCategoryViewSet(TenantViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.IsAuthenticated, BusinessManagerPermission]
    search_fields = ['name', 'description']
    filterset_fields = ['is_active']
    ordering = ['order', 'name']
    
    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        category = self.get_object()
        services = category.services.filter(is_active=True)
        serializer = ServiceListSerializer(services, many=True)
        return success_response(data=serializer.data)


class ServiceViewSet(TenantViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated, BusinessStaffPermission]
    search_fields = ['name', 'description']
    filterset_fields = ['category', 'is_active', 'online_booking_enabled', 'voice_booking_enabled']
    ordering = ['order', 'name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ServiceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ServiceUpdateSerializer
        elif self.action == 'list':
            return ServiceListSerializer
        return ServiceSerializer
    
    @action(detail=True, methods=['get', 'post'])
    def providers(self, request, pk=None):
        service = self.get_object()
        
        if request.method == 'GET':
            providers = service.providers.filter(is_active=True)
            serializer = ServiceProviderSerializer(providers, many=True)
            return success_response(data=serializer.data)
        
        elif request.method == 'POST':
            user_id = request.data.get('user_id')
            is_primary = request.data.get('is_primary', False)
            
            if not user_id:
                return error_response(message="User ID is required")
            
            try:
                from apps.users.models import User
                user = User.objects.get(id=user_id)
                
                if is_primary:
                    ServiceProvider.objects.filter(service=service).update(is_primary=False)
                
                provider, created = ServiceProvider.objects.get_or_create(
                    service=service,
                    user=user,
                    defaults={'is_primary': is_primary, 'is_active': True}
                )
                
                if not created:
                    provider.is_primary = is_primary
                    provider.is_active = True
                    provider.save()
                
                serializer = ServiceProviderSerializer(provider)
                return success_response(
                    data=serializer.data,
                    message="Provider added successfully"
                )
            except User.DoesNotExist:
                return error_response(message="User not found")
    
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        service = self.get_object()
        service.is_active = not service.is_active
        service.save()
        return success_response(
            data={'is_active': service.is_active},
            message=f"Service {'activated' if service.is_active else 'deactivated'}"
        )
    
    @action(detail=False, methods=['get'])
    def public(self, request):
        services = self.get_queryset().filter(
            is_active=True,
            online_booking_enabled=True
        )
        serializer = ServiceListSerializer(services, many=True)
        return success_response(data=serializer.data)


class ServiceProviderViewSet(TenantViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [permissions.IsAuthenticated, BusinessManagerPermission]
    filterset_fields = ['service', 'user', 'is_primary', 'is_active']
    
    def get_queryset(self):
        return ServiceProvider.objects.filter(service__business=self.request.business)
