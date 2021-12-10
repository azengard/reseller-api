from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, CharField
from rest_framework.serializers import ModelSerializer, FloatField, Serializer

from apps.api.purchase.models import Purchase
from apps.api.reseller.models import Reseller


class PurchaseSerializer(ModelSerializer):
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
        extra_kwargs = {'cpf': {'source': 'reseller_cpf', 'read_only': True}}

    def validate(self, data):
        try:
            cpf = self.context['request'].auth['cpf']
            reseller = Reseller.objects.get(cpf=cpf)
            data['reseller_cpf'] = reseller
        except Reseller.DoesNotExist:
            raise ValidationError('Invalid Environment', 'does_not_exist')

        if cpf == Reseller.SPECIAL_RESELLER:
            data.update({'status': Purchase.PurchaseStatus.APPROVED})
        return data

    def get_cashback_percentage(self, obj):
        return obj.get_cashback_percentage()

    def get_cashback_value(self, obj):
        return obj.get_cashback_value()


class CashbackSerializer(Serializer):
    credit = FloatField(required=False)
    message = CharField(required=False)
