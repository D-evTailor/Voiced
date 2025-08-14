from rest_framework.permissions import BasePermission


class TenantPermission(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request, 'business') and request.business is not None
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'business'):
            return obj.business == request.business
        return True


class BusinessPermission(BasePermission):
    required_permission = None
    
    def has_permission(self, request, view):
        if not hasattr(request, 'business') or not request.business:
            return False
        
        member = request.business.members.filter(user=request.user, is_active=True).first()
        if not member:
            return False
            
        return member.has_permission(self.required_permission or 'view_appointments')


class BusinessOwnerPermission(BusinessPermission):
    required_permission = 'all'


class BusinessManagerPermission(BusinessPermission):
    required_permission = 'manage_appointments'


class BusinessStaffPermission(BusinessPermission):
    required_permission = 'view_appointments'
