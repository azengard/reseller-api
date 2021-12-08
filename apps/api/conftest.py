import pytest
from rest_framework.test import APIClient

from apps.api.reseller.models import Reseller


@pytest.fixture()
def api_client():
    api_client = APIClient()
    return api_client


@pytest.fixture()
def normal_reseller_data():
    return {
        'first_name': 'Will',
        'last_name': 'Smith',
        'cpf': '109.876.543-21',
        'email': 'will.smith@email.com',
        'password': 'secure-password'
    }


@pytest.fixture()
def special_reseller_data(normal_reseller_data):
    special_reseller_data = {**normal_reseller_data, 'email': 'special.reseller@email.com', 'cpf': '153.509.460-56'}
    return special_reseller_data


@pytest.fixture()
def resellers(normal_reseller_data, special_reseller_data):
    normal_reseller = Reseller.objects.create_user(**normal_reseller_data)
    special_reseller = Reseller.objects.create_user(**special_reseller_data)
    resellers = [normal_reseller, special_reseller]
    return resellers


@pytest.fixture()
def reseller_token(api_client, resellers):
    response = api_client.post('/api/token/', data={'email': 'will.smith@email.com', 'password': 'secure-password'})
    return response.data


@pytest.fixture
def auth_api_client(api_client, reseller_token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reseller_token['access']}")
    return api_client
