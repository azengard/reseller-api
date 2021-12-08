from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.api.purchase.models import Purchase
from apps.api.purchase.serializers import PurchaseSerializer


class PurchaseViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = PurchaseSerializer
    queryset = Purchase.objects.all()

    lookup_field = 'purchase_uuid'
    lookup_url_kwarg = 'purchase_uuid'
