from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import BaseModel


class BusinessDashboardConfig(BaseModel):
    business = models.OneToOneField('businesses.Business', on_delete=models.CASCADE, related_name='dashboard_config')
    primary_color = models.CharField(_('primary color'), max_length=7, default='#3B82F6')
    secondary_color = models.CharField(_('secondary color'), max_length=7, default='#1E40AF')
    logo_url = models.URLField(_('logo URL'), blank=True)
    welcome_message = models.TextField(_('welcome message'), blank=True)
    show_booking_widget = models.BooleanField(_('show booking widget'), default=True)
    show_services = models.BooleanField(_('show services'), default=True)
    show_contact_info = models.BooleanField(_('show contact info'), default=True)
    custom_css = models.TextField(_('custom CSS'), blank=True)
    
    class Meta:
        verbose_name = _('Business Dashboard Config')
        verbose_name_plural = _('Business Dashboard Configs')
        db_table = 'business_dashboard_configs'
    
    def __str__(self):
        return f"{self.business.name} - Dashboard Config"


class BusinessOnboardingStatus(BaseModel):
    business = models.OneToOneField('businesses.Business', on_delete=models.CASCADE, related_name='onboarding_status')
    
    basic_info_completed = models.BooleanField(_('basic info completed'), default=False)
    services_configured = models.BooleanField(_('services configured'), default=False)
    business_hours_set = models.BooleanField(_('business hours set'), default=False)
    vapi_configured = models.BooleanField(_('vapi configured'), default=False)
    first_appointment_received = models.BooleanField(_('first appointment received'), default=False)
    
    onboarding_completed = models.BooleanField(_('onboarding completed'), default=False)
    onboarding_completed_at = models.DateTimeField(_('onboarding completed at'), null=True, blank=True)
    
    current_step = models.CharField(_('current step'), max_length=50, default='basic_info')
    
    class Meta:
        verbose_name = _('Business Onboarding Status')
        verbose_name_plural = _('Business Onboarding Statuses')
        db_table = 'business_onboarding_statuses'
    
    def __str__(self):
        return f"{self.business.name} - Onboarding: {self.current_step}"
    
    def mark_step_completed(self, step):
        setattr(self, f"{step}_completed", True)
        self._update_current_step()
        self.save()
    
    def _update_current_step(self):
        steps = [
            'basic_info',
            'services_configured', 
            'business_hours_set',
            'vapi_configured'
        ]
        
        for step in steps:
            if not getattr(self, f"{step}_completed"):
                self.current_step = step
                return
        
        if not self.onboarding_completed:
            self.onboarding_completed = True
            from django.utils import timezone
            self.onboarding_completed_at = timezone.now()
            self.current_step = 'completed'
