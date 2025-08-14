from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'vapi_integration'

router = DefaultRouter()
router.register(r'configs', views.VapiConfigViewSet, basename='config')

urlpatterns = [
    # Vapi webhook endpoints
    path('webhooks/call-status/', views.CallStatusWebhookView.as_view(), name='call_status_webhook'),
    path('webhooks/appointment/', views.AppointmentWebhookView.as_view(), name='appointment_webhook'),
    
    # Vapi function tools
    path('tools/get-availability/', views.GetAvailabilityToolView.as_view(), name='get_availability_tool'),
    path('tools/book-appointment/', views.BookAppointmentToolView.as_view(), name='book_appointment_tool'),
    path('tools/get-services/', views.GetServicesToolView.as_view(), name='get_services_tool'),
    
    path('', include(router.urls)),
]
