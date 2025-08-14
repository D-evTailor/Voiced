from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.conf import settings
from apps.businesses.models import Business
from apps.users.models import LoginAttempt
import time


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


class RateLimitMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        if request.path.startswith('/api/auth/login/'):
            return self._check_login_rate_limit(request)
        return None
    
    def _check_login_rate_limit(self, request):
        ip_address = self._get_client_ip(request)
        email = request.POST.get('email') or request.data.get('email') if hasattr(request, 'data') else None
        
        current_time = int(time.time())
        
        if email:
            email_failures = LoginAttempt.get_recent_failures_for_email(email, 15)
            if email_failures >= 5:
                return JsonResponse({
                    'error': 'Too many failed attempts for this email. Please try again in 15 minutes.'
                }, status=429)
        
        ip_failures = LoginAttempt.get_recent_failures_for_ip(ip_address, 15)
        
        if ip_failures >= 10:
            return JsonResponse({
                'error': 'Too many failed attempts from this IP. Please try again in 15 minutes.'
            }, status=429)
        
        return None
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
