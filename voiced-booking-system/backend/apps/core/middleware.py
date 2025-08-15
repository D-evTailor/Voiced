from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from apps.businesses.models import Business
from apps.users.models import LoginAttempt
from .constants import RATE_LIMIT_CONFIG, USER_AGENT_MAX_LENGTH


class BaseMiddleware(MiddlewareMixin):
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class TenantMiddleware(BaseMiddleware):
    def process_request(self, request):
        business = None
        
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            business_id = request.headers.get('X-Business-ID')
            if business_id:
                try:
                    business = Business.objects.get(
                        id=business_id,
                        members__user=request.user
                    )
                except Business.DoesNotExist:
                    pass
            
            if not business:
                membership = request.user.business_memberships.filter(is_primary=True).first()
                if membership:
                    business = membership.business
        
        request.business = business
        return None


class AuditMiddleware(BaseMiddleware):
    def process_request(self, request):
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            user_agent = request.headers.get('User-Agent', '')[:USER_AGENT_MAX_LENGTH]
            request.audit_data = {
                'user_id': request.user.id,
                'user_email': request.user.email,
                'ip_address': self.get_client_ip(request),
                'user_agent': user_agent,
                'business_id': getattr(request, 'business', None) and request.business.id
            }
        return None


class RateLimitMiddleware(BaseMiddleware):
    def process_request(self, request):
        if request.path.startswith('/api/auth/login/'):
            return self._check_login_rate_limit(request)
        return None
    
    def _check_login_rate_limit(self, request):
        ip_address = self.get_client_ip(request)
        email = self._get_email_from_request(request)
        
        window_minutes = RATE_LIMIT_CONFIG['window_minutes']
        
        if email:
            email_failures = LoginAttempt.get_recent_failures_for_email(email, window_minutes)
            if email_failures >= RATE_LIMIT_CONFIG['email_attempts']:
                return self._rate_limit_response('email', window_minutes)
        
        ip_failures = LoginAttempt.get_recent_failures_for_ip(ip_address, window_minutes)
        if ip_failures >= RATE_LIMIT_CONFIG['ip_attempts']:
            return self._rate_limit_response('IP', window_minutes)
        
        return None
    
    def _get_email_from_request(self, request):
        if hasattr(request, 'data'):
            return request.data.get('email')
        return request.POST.get('email')
    
    def _rate_limit_response(self, limit_type, minutes):
        return JsonResponse({
            'error': f'Too many failed attempts for this {limit_type}. Please try again in {minutes} minutes.'
        }, status=429)


class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
        }
        
        if not settings.DEBUG:
            headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        for header, value in headers.items():
            response[header] = value
        
        return response


class ErrorHandlingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        return None
