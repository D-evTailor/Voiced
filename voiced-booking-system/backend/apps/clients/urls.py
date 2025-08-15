from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'clients'

router = DefaultRouter()
router.register('', views.ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
]
