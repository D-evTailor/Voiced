from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.core.viewsets import BaseViewSet, TenantViewSet, OptimizedViewSetMixin
from apps.core.permissions import BusinessOwnerPermission, BusinessManagerPermission
from apps.core.exceptions import success_response, error_response
from .models import Business, BusinessHours, BusinessMember
from .serializers import (
    BusinessSerializer, BusinessCreateSerializer, BusinessUpdateSerializer,
    BusinessHoursSerializer, BusinessMemberSerializer, BusinessListSerializer,
    AdditionalBusinessSerializer
)
from .onboarding_serializers import BusinessDashboardConfigSerializer, BusinessOnboardingStatusSerializer


class BusinessViewSet(OptimizedViewSetMixin, BaseViewSet):
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'email', 'city']
    filterset_fields = ['is_active', 'locale', 'currency', 'subscription_status']
    select_related_fields = ['owner']
    prefetch_related_fields = ['business_hours', 'members__user']
    
    def get_queryset(self):
        return Business.objects.filter(
            members__user=self.request.user,
            members__is_active=True
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'my_businesses':
            return BusinessListSerializer
        elif self.action == 'create_additional':
            return AdditionalBusinessSerializer
        elif self.action == 'create':
            return BusinessCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BusinessUpdateSerializer
        return BusinessSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_businesses(self, request):
        businesses = self.get_queryset()
        serializer = self.get_serializer(businesses, many=True)
        return success_response(data=serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_additional(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        business = serializer.save()
        return success_response(
            data={
                'business_slug': business.slug,
                'business_name': business.name,
                'business_id': business.id
            },
            message="Additional business created successfully"
        )
    
    @action(detail=True, methods=['get', 'patch'])
    def dashboard_config(self, request, pk=None):
        business = self.get_object()
        config = business.dashboard_config
        
        if request.method == 'GET':
            serializer = BusinessDashboardConfigSerializer(config)
            return success_response(data=serializer.data)
        
        serializer = BusinessDashboardConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Dashboard config updated")
    
    @action(detail=True, methods=['get'])
    def onboarding_status(self, request, pk=None):
        business = self.get_object()
        status = business.onboarding_status
        serializer = BusinessOnboardingStatusSerializer(status)
        return success_response(data=serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[BusinessOwnerPermission])
    def add_member(self, request, pk=None):
        business = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'staff')
        
        if not user_id:
            return error_response(message="User ID is required")
        
        try:
            from apps.users.models import User
            user = User.objects.get(id=user_id)
            member, created = BusinessMember.objects.get_or_create(
                business=business,
                user=user,
                defaults={'role': role, 'is_active': True}
            )
            if not created:
                member.role = role
                member.is_active = True
                member.save()
            
            serializer = BusinessMemberSerializer(member)
            return success_response(
                data=serializer.data,
                message="Member added successfully"
            )
        except User.DoesNotExist:
            return error_response(message="User not found")


class BusinessHoursViewSet(TenantViewSet):
    queryset = BusinessHours.objects.all()
    serializer_class = BusinessHoursSerializer
    permission_classes = [permissions.IsAuthenticated, BusinessManagerPermission]
    filterset_fields = ['day_of_week', 'is_closed']
    
    def get_queryset(self):
        return BusinessHours.objects.filter(business=self.request.business)


class BusinessMemberViewSet(TenantViewSet):
    queryset = BusinessMember.objects.all()
    serializer_class = BusinessMemberSerializer
    permission_classes = [permissions.IsAuthenticated, BusinessOwnerPermission]
    filterset_fields = ['role', 'is_active', 'is_primary']
    
    def get_queryset(self):
        return BusinessMember.objects.filter(business=self.request.business)
