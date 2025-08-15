from rest_framework import permissions
from rest_framework.decorators import action
from apps.core.viewsets import TenantViewSet, OptimizedViewSetMixin
from apps.core.permissions import BusinessManagerPermission, BusinessStaffPermission
from apps.core.exceptions import success_response, error_response
from apps.core.status_actions import StatusActionsMixin, FilterActionsMixin
from .models import Service, ServiceCategory, ServiceProvider
from .serializers import (
    ServiceSerializer, ServiceCreateSerializer, ServiceUpdateSerializer,
    ServiceListSerializer, ServiceCategorySerializer, ServiceProviderSerializer
)


class ServiceCategoryViewSet(FilterActionsMixin, TenantViewSet):
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


class ServiceViewSet(OptimizedViewSetMixin, StatusActionsMixin, FilterActionsMixin, TenantViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated, BusinessStaffPermission]
    search_fields = ['name', 'description']
    filterset_fields = ['category', 'is_active', 'online_booking_enabled', 'voice_booking_enabled']
    ordering = ['order', 'name']
    select_related_fields = ['category', 'business']
    prefetch_related_fields = ['providers__user', 'resources']
    
    def get_serializer_class(self):
        serializer_map = {
            'create': ServiceCreateSerializer,
            'update': ServiceUpdateSerializer,
            'partial_update': ServiceUpdateSerializer,
            'list': ServiceListSerializer,
        }
        return serializer_map.get(self.action, ServiceSerializer)
    
    @action(detail=True, methods=['get', 'post'])
    def providers(self, request, pk=None):
        service = self.get_object()
        
        if request.method == 'GET':
            providers = service.providers.filter(is_active=True)
            serializer = ServiceProviderSerializer(providers, many=True)
            return success_response(data=serializer.data)
        
        return self._add_provider(service, request.data)
    
    @action(detail=False, methods=['get'])
    def public(self, request):
        services = self.get_queryset().filter(
            is_active=True,
            online_booking_enabled=True
        )
        serializer = ServiceListSerializer(services, many=True)
        return success_response(data=serializer.data)
    
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        result = self.toggle_active_action(request, pk)
        return success_response(data={'is_active': result['is_active']}, message=result['message'])
    
    def _add_provider(self, service, data):
        user_id = data.get('user_id')
        is_primary = data.get('is_primary', False)
        
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
                provider.save(update_fields=['is_primary', 'is_active'])
            
            serializer = ServiceProviderSerializer(provider)
            return success_response(
                data=serializer.data,
                message="Provider added successfully"
            )
        except User.DoesNotExist:
            return error_response(message="User not found")


class ServiceProviderViewSet(TenantViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [permissions.IsAuthenticated, BusinessManagerPermission]
    filterset_fields = ['service', 'user', 'is_primary', 'is_active']
    
    def get_queryset(self):
        return ServiceProvider.objects.filter(service__business=self.request.business)
