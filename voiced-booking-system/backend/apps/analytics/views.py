from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from apps.core.permissions import TenantPermission


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, TenantPermission]
    
    def get(self, request):
        return Response({
            'total_appointments': 0,
            'revenue': 0,
            'active_clients': 0,
            'message': 'Analytics dashboard - not implemented yet'
        })


class BusinessMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, TenantPermission]
    
    def list(self, request):
        return Response({
            'metrics': [],
            'message': 'Business metrics - not implemented yet'
        })


class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated, TenantPermission]
    
    def get(self, request):
        return Response({
            'total_appointments': 0,
            'revenue': 0,
            'active_clients': 0,
            'message': 'Analytics view - not implemented yet'
        })
