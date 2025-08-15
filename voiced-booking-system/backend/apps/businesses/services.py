from django.db import transaction
from django.utils.text import slugify
from apps.users.models import User
from .models import Business, BusinessMember
from .onboarding_models import BusinessOnboardingStatus
from apps.vapi_integration.tasks import register_tenant_async


class BusinessRegistrationService:
    @transaction.atomic
    def create_user_with_business(self, user_data, business_data):
        user = User.objects.create_user(**user_data)
        
        business_data['slug'] = self._generate_unique_slug(business_data['name'])
        business_data['owner'] = user
        business = Business.objects.create(**business_data)
        
        BusinessMember.objects.create(
            business=business,
            user=user,
            role='owner',
            is_primary=True,
            is_active=True
        )
        
        business.onboarding_status.mark_step_completed('basic_info')
        
        register_tenant_async.delay(business.id)
        
        return user, business
    
    @transaction.atomic
    def create_additional_business(self, user, business_data):
        business_data['slug'] = self._generate_unique_slug(business_data['name'])
        business_data['owner'] = user
        business = Business.objects.create(**business_data)
        
        BusinessMember.objects.create(
            business=business,
            user=user,
            role='owner',
            is_primary=False,
            is_active=True
        )
        
        business.onboarding_status.mark_step_completed('basic_info')
        
        register_tenant_async.delay(business.id)
        
        return business
    
    def _generate_unique_slug(self, name):
        base_slug = slugify(name)[:45]
        slug = base_slug
        counter = 1
        
        while Business.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
