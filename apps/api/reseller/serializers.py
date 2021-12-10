from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from apps.api.reseller.models import Reseller
from apps.api.validators import cpf_validator


class ResellerSerializer(ModelSerializer):
    cpf = CharField(validators=[cpf_validator])

    class Meta:
        model = Reseller
        fields = ['email', 'first_name', 'last_name', 'cpf', 'password']
        extra_kwargs = {'password': {'write_only': True}}
