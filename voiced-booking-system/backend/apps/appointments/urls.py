from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'appointments'

router = DefaultRouter()
router.register('', views.AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('availability/', views.AvailabilityView.as_view(), name='availability'),
    path('', include(router.urls)),
]
