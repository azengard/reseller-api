from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.api.purchase.serializers import PurchaseSerializer


class PurchaseViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = PurchaseSerializer
