from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import TenantPermission
from .pagination import StandardResultsSetPagination
from .serializers import TenantFilteredSerializer


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, TenantPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return self.queryset.filter(business=self.request.business)
    
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            business=self.request.business
        )
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        if hasattr(instance, 'delete'):
            instance.delete(user=self.request.user)
        else:
            instance.delete()
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        instance = self.get_object()
        if hasattr(instance, 'restore'):
            instance.restore()
            return Response({'status': 'restored'})
        return Response({'error': 'Object cannot be restored'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False)
    def deleted(self, request):
        model = self.get_queryset().model
        if hasattr(model, 'all_objects'):
            queryset = model.all_objects.filter(
                business=request.business,
                deleted_at__isnull=False
            )
        else:
            return Response({'error': 'Soft delete not supported'}, status=status.HTTP_400_BAD_REQUEST)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TenantViewSet(BaseViewSet):
    serializer_class = TenantFilteredSerializer


class ReadOnlyTenantViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated, TenantPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return self.queryset.filter(business=self.request.business)


class OptimizedViewSetMixin:
    select_related_fields = []
    prefetch_related_fields = []
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)
        return queryset
