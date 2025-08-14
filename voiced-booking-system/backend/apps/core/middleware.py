from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from apps.businesses.models import Business


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        business = None
        
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            business_id = request.headers.get('X-Business-ID')
            if business_id:
                try:
                    business = Business.objects.get(
                        id=business_id,
                        tenant_users__user=request.user
                    )
                except Business.DoesNotExist:
                    pass
            
            if not business:
                tenant_user = request.user.tenant_users.filter(is_primary=True).first()
                if tenant_user:
                    business = tenant_user.business
        
        request.business = business
        return None


class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            request.audit_data = {
                'user_id': request.user.id,
                'user_email': request.user.email,
                'ip_address': self.get_client_ip(request),
                'user_agent': request.headers.get('User-Agent', ''),
                'business_id': getattr(request, 'business', None) and request.business.id
            }
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ErrorHandlingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if hasattr(request, 'audit_data'):
            pass
        return None
