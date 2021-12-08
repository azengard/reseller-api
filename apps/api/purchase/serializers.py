from rest_framework.serializers import ModelSerializer, FloatField

from apps.api.purchase.models import Purchase
from apps.api.reseller.models import Reseller
from apps.api.serializers import UniqueRelatedField


class PurchaseSerializer(ModelSerializer):
    cpf = UniqueRelatedField(source='reseller_cpf', field_name='cpf', queryset=Reseller.objects.all(), required=True)
    value = FloatField()

    class Meta:
        model = Purchase
        fields = ['purchase_uuid', 'cpf', 'code', 'value', 'purchase_date', 'status']

    def validate(self, data):
        if data.get('reseller_cpf').cpf == Reseller.SPECIAL_RESELLER:
            data.update({'status': Purchase.PurchaseStatus.APPROVED})
        return data
