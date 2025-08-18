from apps.core.cache import cache_service
from functools import wraps
from typing import Any, Dict, Optional, Union, Callable
from django.core.cache import cache
from django.utils import timezone
import hashlib
import inspect


class VapiCacheKeys:
    PREFIX = "vapi"
    
    @classmethod
    def business_config(cls, business_id: int) -> str:
        return f"{cls.PREFIX}:config:{business_id}"
    
    @classmethod
    def assistant(cls, business_id: int) -> str:
        return f"{cls.PREFIX}:assistant:{business_id}"
    
    @classmethod
    def services(cls, business_id: int) -> str:
        return f"{cls.PREFIX}:services:{business_id}"
    
    @classmethod
    def availability(cls, business_id: int, service_id: int, date: str) -> str:
        return f"{cls.PREFIX}:availability:{business_id}:{service_id}:{date}"
    
    @classmethod
    def call_analysis(cls, call_id: str) -> str:
        return f"{cls.PREFIX}:analysis:{call_id}"
    
    @classmethod
    def business_pattern(cls, business_id: int) -> str:
        return f"{cls.PREFIX}:*:{business_id}:*"


class VapiCacheService:
    def __init__(self, cache_service):
        self._cache = cache_service
        self.DEFAULT_TTL = 3600
        
    def get(self, key: str) -> Any:
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        self._cache.set(key, value, ttl or self.DEFAULT_TTL)
    
    def delete(self, key: str) -> None:
        self._cache.delete(key)
    
    def invalidate_pattern(self, pattern: str) -> None:
        self._cache.invalidate_pattern(pattern)
    
    def get_or_set(self, key: str, default_func, ttl: int = None) -> Any:
        value = self.get(key)
        if value is None:
            value = default_func()
            self.set(key, value, ttl)
        return value


def cached_method(timeout: int = 3600, key_func: Optional[Callable] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                key_data = f"{func.__module__}.{func.__name__}:{bound_args.arguments}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def circuit_breaker(max_failures: int = 5, timeout: int = 60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"circuit_breaker:{func.__module__}.{func.__name__}"
            failures = cache.get(f"{cache_key}:failures", 0)
            
            if failures >= max_failures:
                last_failure = cache.get(f"{cache_key}:last_failure")
                if last_failure and (timezone.now().timestamp() - last_failure) < timeout:
                    raise Exception("Circuit breaker is open")
                else:
                    cache.delete(f"{cache_key}:failures")
                    cache.delete(f"{cache_key}:last_failure")
            
            try:
                result = func(*args, **kwargs)
                cache.delete(f"{cache_key}:failures")
                return result
            except Exception as e:
                cache.set(f"{cache_key}:failures", failures + 1, timeout * 2)
                cache.set(f"{cache_key}:last_failure", timezone.now().timestamp(), timeout * 2)
                raise e
        return wrapper
    return decorator


vapi_cache_service = VapiCacheService(cache_service)


def vapi_cache(ttl: int = 3600, key_func=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"vapi:func:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            return vapi_cache_service.get_or_set(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl
            )
        return wrapper
    return decorator


class VapiConfigManager:
    @staticmethod
    @vapi_cache(ttl=1800, key_func=lambda business_id: VapiCacheKeys.business_config(business_id))
    def get_business_config(business_id: int) -> Optional[Dict]:
        from .models import VapiConfiguration
        try:
            config = VapiConfiguration.objects.select_related('business').get(
                business_id=business_id, is_active=True
            )
            return {
                'assistant_id': config.assistant_id,
                'phone_number_id': config.phone_number_id,
                'server_url': config.server_url,
                'server_secret': config.server_secret,
                'assistant_config': config.assistant_config,
                'metadata': config.metadata,
            }
        except VapiConfiguration.DoesNotExist:
            return None
    
    @staticmethod
    @vapi_cache(ttl=900, key_func=lambda business_id: VapiCacheKeys.assistant(business_id))
    def get_assistant_config(business_id: int) -> Optional[Dict]:
        config = VapiConfigManager.get_business_config(business_id)
        return config.get('assistant_config') if config else None
    
    @staticmethod
    def invalidate_business_cache(business_id: int):
        vapi_cache_service.invalidate_pattern(VapiCacheKeys.business_pattern(business_id))


class VapiAnalyticsOptimizer:
    @staticmethod
    @vapi_cache(ttl=600)
    def get_call_metrics(business_id: int, date_from: str, date_to: str) -> Dict:
        from .models import VapiUsageMetrics
        from django.db.models import Sum, Avg
        
        metrics = VapiUsageMetrics.objects.filter(
            business_id=business_id,
            date__range=[date_from, date_to]
        ).aggregate(
            total_calls=Sum('total_calls'),
            total_minutes=Sum('total_minutes'),
            total_cost=Sum('estimated_cost'),
            successful_bookings=Sum('successful_bookings'),
            failed_bookings=Sum('failed_bookings'),
            avg_call_duration=Avg('total_minutes')
        )
        
        return {k: v or 0 for k, v in metrics.items()}
    
    @staticmethod
    def update_daily_metrics(business_id: int, date: str, **metrics):
        from .models import VapiUsageMetrics
        from django.utils.dateparse import parse_date
        
        date_obj = parse_date(date)
        usage, created = VapiUsageMetrics.objects.get_or_create(
            business_id=business_id,
            date=date_obj,
            defaults=metrics
        )
        
        if not created:
            for key, value in metrics.items():
                if hasattr(usage, key):
                    setattr(usage, key, getattr(usage, key, 0) + value)
            usage.save()
        
        vapi_cache_service.delete(f"vapi:metrics:{business_id}")


class VapiDataProcessor:
    @staticmethod
    def normalize_phone_number(phone: str) -> str:
        import re
        return re.sub(r'[^\d+]', '', phone)
    
    @staticmethod
    def extract_booking_data(transcript: str) -> Dict:
        return {}
    
    @staticmethod
    def calculate_call_cost(duration_seconds: int, provider: str = 'default') -> float:
        COST_PER_MINUTE = {
            'default': 0.05,
            'openai': 0.06,
            'elevenlabs': 0.08
        }
        
        minutes = duration_seconds / 60
        rate = COST_PER_MINUTE.get(provider, COST_PER_MINUTE['default'])
        return round(minutes * rate, 4)
