import hashlib
import hmac
import time
from typing import Optional
from django.core.cache import cache
from django.conf import settings
from django.http import HttpRequest
import logging

logger = logging.getLogger(__name__)


class VapiSecurityService:
    def __init__(self, secret: str):
        self.secret = secret
    
    def validate_webhook_signature(self, request: HttpRequest, body: bytes) -> bool:
        signature = request.headers.get('X-Vapi-Signature')
        if not signature:
            logger.warning(f"Missing X-Vapi-Signature header from {request.META.get('REMOTE_ADDR')}")
            return False
        
        expected_signature = self._generate_signature(body)
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if not is_valid:
            logger.warning(f"Invalid webhook signature from {request.META.get('REMOTE_ADDR')}")
        
        return is_valid
    
    def _generate_signature(self, body: bytes) -> str:
        return hmac.new(
            self.secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()


class WebhookRateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, identifier: str) -> bool:
        cache_key = f"vapi_webhook_rate_limit:{identifier}"
        current_count = cache.get(cache_key, 0)
        
        if current_count >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        cache.set(cache_key, current_count + 1, self.window_seconds)
        return True


class WebhookSecurityManager:
    def __init__(self, business):
        self.business = business
        self.security_service = self._get_security_service()
        self.rate_limiter = WebhookRateLimiter()
    
    def _get_security_service(self) -> Optional[VapiSecurityService]:
        try:
            config = self.business.vapi_configurations.filter(is_active=True).first()
            if config and config.server_secret:
                return VapiSecurityService(config.server_secret)
        except Exception as e:
            logger.error(f"Error getting security service for business {self.business.id}: {e}")
        return None
    
    def validate_request(self, request: HttpRequest, body: bytes) -> bool:
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        if not self.rate_limiter.is_allowed(f"{self.business.id}:{client_ip}"):
            return False
        
        if self.security_service:
            return self.security_service.validate_webhook_signature(request, body)
        
        logger.warning(f"No security configuration for business {self.business.id}")
        return True
