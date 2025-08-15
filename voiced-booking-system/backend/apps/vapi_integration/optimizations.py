from apps.core.cache import cache_service


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
