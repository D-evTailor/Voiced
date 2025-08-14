from functools import wraps
from typing import Any, Callable, Optional
from django.core.cache import cache
from django.conf import settings
import time
import logging

logger = logging.getLogger(__name__)


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == 'OPEN':
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                else:
                    logger.warning(f"Circuit breaker OPEN for {func.__name__}")
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _on_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.error(f"Circuit breaker opened after {self.failure_count} failures")


class CacheService:
    def __init__(self, default_timeout: int = 300):
        self.default_timeout = default_timeout
    
    def get_or_set(self, key: str, callable_func: Callable, timeout: Optional[int] = None) -> Any:
        result = cache.get(key)
        if result is None:
            result = callable_func()
            cache.set(key, result, timeout or self.default_timeout)
        return result
    
    def invalidate_pattern(self, pattern: str):
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
        else:
            cache.clear()
    
    def get_business_config_key(self, business_id: int) -> str:
        return f"vapi_config:{business_id}"
    
    def get_services_key(self, business_id: int) -> str:
        return f"vapi_services:{business_id}"
    
    def get_availability_key(self, business_id: int, service_id: int, date: str) -> str:
        return f"vapi_availability:{business_id}:{service_id}:{date}"


def cached_method(timeout: int = 300, key_func: Optional[Callable] = None):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if key_func:
                cache_key = key_func(self, *args, **kwargs)
            else:
                cache_key = f"{self.__class__.__name__}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            result = cache.get(cache_key)
            if result is None:
                result = func(self, *args, **kwargs)
                cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


circuit_breaker = CircuitBreaker()
cache_service = CacheService()
