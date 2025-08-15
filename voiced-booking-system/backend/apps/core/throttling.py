from rest_framework.throttling import SimpleRateThrottle, UserRateThrottle
from django.core.cache import cache
import time


class BurstRateThrottle(SimpleRateThrottle):
    scope = 'burst'
    
    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class SustainedRateThrottle(SimpleRateThrottle):
    scope = 'sustained'
    
    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class WebhookRateThrottle(SimpleRateThrottle):
    scope = 'webhook'
    
    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class APIKeyRateThrottle(SimpleRateThrottle):
    scope = 'api_key'
    
    def get_cache_key(self, request, view):
        api_key = request.headers.get('X-API-Key')
        if api_key:
            ident = api_key[:10]
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class BusinessAwareRateThrottle(UserRateThrottle):
    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        
        business_id = getattr(request, 'business', None) and request.business.id
        ident = f"{request.user.pk}:{business_id}"
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class AdaptiveRateThrottle(SimpleRateThrottle):
    def allow_request(self, request, view):
        if request.user and request.user.is_authenticated:
            if hasattr(request.user, 'is_premium') and request.user.is_premium:
                self.rate = '10000/hour'
            else:
                self.rate = '1000/hour'
        else:
            self.rate = '100/hour'
        
        if not self.rate:
            return True
        
        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True
        
        self.history = self.cache.get(self.key, [])
        self.now = self.timer()
        
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        
        return self.throttle_success()
    
    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': 'adaptive',
            'ident': ident
        }
