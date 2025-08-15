from functools import wraps
from typing import Any, Callable, Optional
from django.core.cache import cache
import time
import logging

logger = logging.getLogger(__name__)


class VapiCacheKeys:
    @staticmethod
    def business_config(business_id: int) -> str:
        return f"vapi:config:{business_id}"
    
    @staticmethod
    def services(business_id: int) -> str:
        return f"vapi:services:{business_id}"
    
    @staticmethod
    def availability(business_id: int, service_id: int, date: str) -> str:
        return f"vapi:availability:{business_id}:{service_id}:{date}"
    
    @staticmethod
    def business_pattern(business_id: int) -> str:
        return f"vapi:*:{business_id}:*"


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
    
    def invalidate_business_cache(self, business_id: int):
        self.invalidate_pattern(VapiCacheKeys.business_pattern(business_id))


class CircuitBreaker:
    def __init__(self, max_failures: int = 3):
        self.max_failures = max_failures
        self.failure_count = 0
        self.is_open = False
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.is_open and self.failure_count >= self.max_failures:
                logger.warning(f"Circuit breaker OPEN for {func.__name__}")
                raise Exception(f"Service temporarily unavailable")
            
            try:
                result = func(*args, **kwargs)
                self.failure_count = 0
                self.is_open = False
                return result
            except Exception as e:
                self.failure_count += 1
                if self.failure_count >= self.max_failures:
                    self.is_open = True
                raise e
        return wrapper


def cached_method(timeout: int = 300, key_func: Optional[Callable] = None):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if key_func:
                cache_key = key_func(self, *args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            result = cache.get(cache_key)
            if result is None:
                result = func(self, *args, **kwargs)
                cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


cache_service = CacheService()
circuit_breaker = CircuitBreaker()
