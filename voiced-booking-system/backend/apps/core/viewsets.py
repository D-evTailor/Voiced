from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import TenantPermission, BusinessOwnerPermission
from .pagination import StandardResultsSetPagination
from .serializers import BaseSerializer, TenantFilteredSerializer


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
        instance.delete(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        instance = self.get_object()
        instance.restore()
        return Response({'status': 'restored'})
    
    @action(detail=False)
    def deleted(self, request):
        queryset = self.get_queryset().model.all_objects.filter(
            business=request.business,
            deleted_at__isnull=False
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TenantViewSet(BaseViewSet):
    serializer_class = TenantFilteredSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['business'] = self.request.business
        return context


class ReadOnlyTenantViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated, TenantPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return self.queryset.filter(business=self.request.business)
