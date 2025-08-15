from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.core.cache import cache
import hashlib
import hmac
import time

User = get_user_model()


class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return None
        
        try:
            user = self._get_user_from_api_key(api_key)
            if user and user.is_active:
                return (user, None)
        except Exception:
            pass
        
        raise exceptions.AuthenticationFailed('Invalid API key')
    
    def _get_user_from_api_key(self, api_key):
        cache_key = f'api_key:{hashlib.sha256(api_key.encode()).hexdigest()}'
        user_id = cache.get(cache_key)
        
        if user_id:
            try:
                return User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                cache.delete(cache_key)
        
        return None


class SignatureAuthentication(BaseAuthentication):
    def authenticate(self, request):
        signature = request.headers.get('X-Signature')
        timestamp = request.headers.get('X-Timestamp')
        
        if not signature or not timestamp:
            return None
        
        try:
            timestamp_int = int(timestamp)
            current_time = int(time.time())
            
            if abs(current_time - timestamp_int) > 300:
                raise exceptions.AuthenticationFailed('Request timestamp too old')
            
            expected_signature = self._calculate_signature(request, timestamp)
            if not hmac.compare_digest(signature, expected_signature):
                raise exceptions.AuthenticationFailed('Invalid signature')
            
            return (None, 'webhook')
            
        except (ValueError, TypeError):
            raise exceptions.AuthenticationFailed('Invalid timestamp')
    
    def _calculate_signature(self, request, timestamp):
        from django.conf import settings
        secret = getattr(settings, 'WEBHOOK_SECRET', '')
        
        body = getattr(request, 'body', b'')
        if isinstance(body, str):
            body = body.encode('utf-8')
        
        message = f"{timestamp}.{body.decode('utf-8', errors='ignore')}"
        return hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
