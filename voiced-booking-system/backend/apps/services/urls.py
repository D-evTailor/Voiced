from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'services'

router = DefaultRouter()
router.register('categories', views.ServiceCategoryViewSet, basename='category')
router.register('services', views.ServiceViewSet, basename='service')
router.register('providers', views.ServiceProviderViewSet, basename='provider')

urlpatterns = [
    path('', include(router.urls)),
]
