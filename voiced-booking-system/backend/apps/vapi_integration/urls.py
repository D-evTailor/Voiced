from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'vapi_integration'

router = DefaultRouter()
router.register(r'configs', views.VapiConfigurationViewSet, basename='config')
router.register(r'calls', views.VapiCallViewSet, basename='call')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', views.VapiWebhookViewSet.as_view({'post': 'create'}), name='webhook'),
    path('business/<int:business_id>/', include([
        path('calls/outbound/', views.VapiCallViewSet.as_view({'post': 'make_outbound_call'}), name='outbound-call'),
        path('configs/<int:pk>/sync-assistant/', views.VapiConfigurationViewSet.as_view({'post': 'sync_assistant'}), name='sync-assistant'),
    ])),
]
