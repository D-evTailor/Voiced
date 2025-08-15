from django.db import transaction
from django.utils.text import slugify
from apps.users.models import User
from .models import Business, BusinessMember
from .onboarding_models import BusinessOnboardingStatus
from apps.vapi_integration.tasks import register_tenant_async


class BusinessRegistrationService:
    @transaction.atomic
    def create_business(self, user=None, user_data=None, business_data=None, is_primary=True):
        if user_data and not user:
            user = User.objects.create_user(**user_data)
        elif not user:
            raise ValueError("Either user or user_data must be provided")
        
        if not business_data:
            raise ValueError("business_data is required")
            
        business_data = business_data.copy()
        business_data['slug'] = self._generate_unique_slug(business_data['name'])
        business_data['owner'] = user
        business = Business.objects.create(**business_data)
        
        BusinessMember.objects.create(
            business=business,
            user=user,
            role='owner',
            is_primary=is_primary,
            is_active=True
        )
        
        business.onboarding_status.mark_step_completed('basic_info')
        register_tenant_async.delay(business.id)
        
        if user_data:
            return user, business
        return business
    
    def _generate_unique_slug(self, name):
        base_slug = slugify(name)[:45]
        slug = base_slug
        counter = 1
        
        while Business.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
