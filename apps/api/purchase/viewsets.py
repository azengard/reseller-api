import logging

import requests
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.api.purchase.exceptions import PurchaseModifyForbiddenException
from apps.api.purchase.models import Purchase
from apps.api.purchase.serializers import PurchaseSerializer, CashbackSerializer
from apps.api.reseller.models import Reseller

log = logging.getLogger(__name__)


class PurchaseViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = PurchaseSerializer
    queryset = Purchase.objects.all()

    lookup_field = 'purchase_uuid'
    lookup_url_kwarg = 'purchase_uuid'

    def get_queryset(self):
        cpf = self.request.auth['cpf']
        reseller = Reseller.objects.get(cpf=cpf)
        qs = reseller.purchases.all()
        return qs

    def get_object(self):
        obj = super().get_object()

        if (obj is not None) and (self.action in ['update', 'partial_update', 'destroy']):
            if obj.status != Purchase.PurchaseStatus.VALIDATING:
                log.warning('Reseller are not allowed to modify a purchase', extra={'cpf': obj.reseller_cpf_id})
                raise PurchaseModifyForbiddenException()
        return obj

    def list(self, request, *args, **kwargs):
        """List all Reseller's Purchases"""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a Purchase"""
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a new Purchase"""
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update a Purchase, this action is available only if purchase status are 'validating'"""
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Partial Update a Purchase, this action is available only if purchase status are 'validating'"""
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete a Purchase, this action is available only if purchase status are 'validating'"""
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['GET'])
    def cashback(self, request, *args, **kwargs):
        """Retrieve the total cashback value earned by the Reseller"""
        url = settings.CASHBACK_API_URL
        headers = {'token': settings.CASHBACK_API_TOKEN}

        cpf = request.auth.payload['cpf']
        cpf = ''.join(char for char in cpf if char.isdigit())
        params = {'cpf': cpf}

        log.info("Calling API to retrieve total reseller's cashback value", extra={'cpf': cpf})
        response = requests.get(url, params=params, headers=headers).json()

        serializer = CashbackSerializer(data=response['body'])
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=response['statusCode'])
