import requests
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.api.purchase.exceptions import PurchaseModifyForbiddenException
from apps.api.purchase.models import Purchase
from apps.api.purchase.serializers import PurchaseSerializer, CashbackResponse


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

    @action(detail=False, methods=['GET'])
    def cashback(self, request, *args, **kwargs):
        url = settings.CASHBACK_API_URL
        headers = {'token': settings.CASHBACK_API_TOKEN}
        params = {'cpf': '12312312323'}
        response = requests.get(url, params=params, headers=headers)

        serializer = CashbackResponse(data={})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
