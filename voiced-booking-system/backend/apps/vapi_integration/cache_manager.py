from .models import VapiCall, VapiConfiguration
from .optimizations import cache_service


class VapiCacheManager:
    @staticmethod
    def invalidate_business_cache(business_id: int):
        cache_service.invalidate_pattern(f"vapi_*:{business_id}:*")
    
    @staticmethod
    def invalidate_config_cache(business_id: int):
        cache_key = cache_service.get_business_config_key(business_id)
        cache_service.invalidate_pattern(cache_key)
    
    @staticmethod
    def invalidate_services_cache(business_id: int):
        cache_key = cache_service.get_services_key(business_id)
        cache_service.invalidate_pattern(cache_key)
    
    @staticmethod
    def warm_cache_for_business(business_id: int):
        try:
            from .domain_services import AvailabilityQueryService
            from apps.businesses.models import Business
            
            business = Business.objects.get(id=business_id)
            service = AvailabilityQueryService(business)
            service.get_available_services()
            
        except Exception:
            pass
