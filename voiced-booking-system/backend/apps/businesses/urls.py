from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'businesses'

router = DefaultRouter()
router.register('businesses', views.BusinessViewSet, basename='business')
router.register('hours', views.BusinessHoursViewSet, basename='business-hours')
router.register('members', views.BusinessMemberViewSet, basename='business-members')

urlpatterns = [
    path('', include(router.urls)),
]
