from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'services'

router = DefaultRouter()
router.register(r'categories', views.ServiceCategoryViewSet, basename='category')
router.register(r'services', views.ServiceViewSet, basename='service')
router.register(r'providers', views.ServiceProviderViewSet, basename='provider')

urlpatterns = [
    path('', include(router.urls)),
]
