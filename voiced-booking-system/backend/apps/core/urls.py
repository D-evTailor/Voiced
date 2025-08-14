from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()

urlpatterns = [
    path('v1/auth/', include('apps.users.urls')),
    path('v1/businesses/', include('apps.businesses.urls')),
    path('v1/services/', include('apps.services.urls')),
    path('v1/appointments/', include('apps.appointments.urls')),
    path('v1/payments/', include('apps.payments.urls')),
    path('v1/vapi/', include('apps.vapi_integration.urls')),
    path('v1/notifications/', include('apps.notifications.urls')),
    path('v1/analytics/', include('apps.analytics.urls')),
    path('v1/resources/', include('apps.resources.urls')),
]
