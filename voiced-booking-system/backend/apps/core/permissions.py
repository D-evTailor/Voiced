from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class TenantPermission(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request, 'business') and request.business is not None
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'business'):
            return obj.business == request.business
        return True


class BusinessOwnerPermission(BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request, 'business'):
            return False
        return request.business.tenant_users.filter(
            user=request.user,
            role__in=['owner', 'admin']
        ).exists()


class BusinessManagerPermission(BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request, 'business'):
            return False
        return request.business.tenant_users.filter(
            user=request.user,
            role__in=['owner', 'admin', 'manager']
        ).exists()


class BusinessStaffPermission(BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request, 'business'):
            return False
        return request.business.tenant_users.filter(user=request.user).exists()
