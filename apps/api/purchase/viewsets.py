from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.api.purchase.exceptions import PurchaseModifyForbiddenException
from apps.api.purchase.models import Purchase
from apps.api.purchase.serializers import PurchaseSerializer


class PurchaseViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = PurchaseSerializer
    queryset = Purchase.objects.all()

    lookup_field = 'purchase_uuid'
    lookup_url_kwarg = 'purchase_uuid'

    def get_object(self):
        obj = super().get_object()

        if (obj is not None) and (self.action in ['update', 'partial_update', 'destroy']):
            if obj.status != Purchase.PurchaseStatus.VALIDATING:
                raise PurchaseModifyForbiddenException()
        return obj
