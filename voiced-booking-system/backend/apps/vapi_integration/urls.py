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
]
