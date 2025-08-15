from apps.core.cache import cache_service, CacheService


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
    def assistant(business_id: int) -> str:
        return f"vapi:assistant:{business_id}"
    
    @staticmethod
    def business_pattern(business_id: int) -> str:
        return f"vapi:*:{business_id}:*"


class VapiCacheService(CacheService):
    def invalidate_business_cache(self, business_id: int):
        self.invalidate_pattern(VapiCacheKeys.business_pattern(business_id))


vapi_cache_service = VapiCacheService()
