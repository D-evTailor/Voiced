from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.core.viewsets import BaseViewSet, TenantViewSet
from apps.core.permissions import BusinessOwnerPermission, BusinessManagerPermission
from apps.core.exceptions import success_response, error_response
from .models import Business, BusinessHours, BusinessMember
from .serializers import (
    BusinessSerializer, BusinessCreateSerializer, BusinessUpdateSerializer,
    BusinessHoursSerializer, BusinessMemberSerializer
)


class BusinessViewSet(BaseViewSet):
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'email', 'city']
    filterset_fields = ['is_active', 'locale', 'currency', 'subscription_status']
    
    def get_queryset(self):
        return Business.objects.filter(
            members__user=self.request.user,
            members__is_active=True
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BusinessCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BusinessUpdateSerializer
        return BusinessSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['get', 'put'])
    def hours(self, request, pk=None):
        business = self.get_object()
        
        if request.method == 'GET':
            hours = business.business_hours.all().order_by('day_of_week')
            serializer = BusinessHoursSerializer(hours, many=True)
            return success_response(data=serializer.data)
        
        elif request.method == 'PUT':
            hours_data = request.data.get('hours', [])
            for hour_data in hours_data:
                day_of_week = hour_data.get('day_of_week')
                hour_obj, created = BusinessHours.objects.get_or_create(
                    business=business,
                    day_of_week=day_of_week,
                    defaults=hour_data
                )
                if not created:
                    for attr, value in hour_data.items():
                        setattr(hour_obj, attr, value)
                    hour_obj.save()
            
            hours = business.business_hours.all().order_by('day_of_week')
            serializer = BusinessHoursSerializer(hours, many=True)
            return success_response(data=serializer.data, message="Business hours updated")
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        business = self.get_object()
        members = business.members.filter(is_active=True)
        serializer = BusinessMemberSerializer(members, many=True)
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
