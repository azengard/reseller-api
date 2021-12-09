from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, FloatField, Serializer

from apps.api.purchase.models import Purchase
from apps.api.reseller.models import Reseller
from apps.api.serializers import UniqueRelatedField


class PurchaseSerializer(ModelSerializer):
    cpf = UniqueRelatedField(source='reseller_cpf', field_name='cpf', queryset=Reseller.objects.all(), required=True)
    value = FloatField()
    cashback_percentage = SerializerMethodField(read_only=True)
    cashback_value = SerializerMethodField(read_only=True)

    class Meta:
        model = Purchase
        fields = ['purchase_uuid',
                  'cpf',
                  'code',
                  'value',
                  'purchase_date',
                  'cashback_percentage',
                  'cashback_value',
                  'status']

    def validate(self, data):
        if data.get('reseller_cpf').cpf == Reseller.SPECIAL_RESELLER:
            data.update({'status': Purchase.PurchaseStatus.APPROVED})
        return data

    def get_cashback_percentage(self, obj):
        return obj.get_cashback_percentage()

    def get_cashback_value(self, obj):
        return obj.get_cashback_value()


class CashbackResponse(Serializer):
    pass
