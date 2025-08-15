from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'services'

router = DefaultRouter()
router.register('categories', views.ServiceCategoryViewSet, basename='categories')
router.register('providers', views.ServiceProviderViewSet, basename='providers')
router.register('', views.ServiceViewSet, basename='service')

urlpatterns = [
    path('', include(router.urls)),
]
