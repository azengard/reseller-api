from rest_framework.serializers import ModelSerializer

from apps.api.reseller.models import Reseller


class ResellerSerializer(ModelSerializer):
    class Meta:
        model = Reseller
        fields = ['email', 'first_name', 'last_name', 'cpf', 'password']
