from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'analytics'

router = DefaultRouter()
router.register(r'metrics', views.BusinessMetricsViewSet, basename='metrics')

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('', include(router.urls)),
]
