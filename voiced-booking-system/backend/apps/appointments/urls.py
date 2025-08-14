from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'appointments'

router = DefaultRouter()
router.register('appointments', views.AppointmentViewSet, basename='appointment')
router.register('clients', views.ClientViewSet, basename='client')

urlpatterns = [
    path('availability/', views.AvailabilityView.as_view(), name='availability'),
    path('', include(router.urls)),
]
