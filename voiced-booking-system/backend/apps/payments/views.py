from rest_framework import viewsets
from apps.core.viewsets import TenantViewSet


class PaymentViewSet(TenantViewSet):
    queryset = None
    serializer_class = None
