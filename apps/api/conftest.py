import pytest
from model_bakery import baker
from rest_framework.test import APIClient

from apps.api.reseller.models import Reseller


@pytest.fixture()
def api_client():
    api_client = APIClient()
    return api_client


@pytest.fixture()
def reseller_data():
    return {
        'first_name': 'Will',
        'last_name': 'Smith',
        'cpf': '109.876.543-21',
        'email': 'will.smith@email.com',
        'password': 'secure-password'
    }


@pytest.fixture()
def special_reseller_data(reseller_data):
    reseller_data.update({'email': 'special.reseller@email.com',
                          'cpf': Reseller.SPECIAL_RESELLER})
    return reseller_data


@pytest.fixture
def reseller(reseller_data):
    return Reseller.objects.create_user(**reseller_data)


@pytest.fixture
def special_reseller(special_reseller_data):
    return Reseller.objects.create_user(**special_reseller_data)


@pytest.fixture()
def reseller_token(api_client, reseller):
    response = api_client.post('/api/token/', data={'email': reseller.email, 'password': 'secure-password'})
    return response.data


@pytest.fixture()
def special_reseller_token(api_client, special_reseller):
    response = api_client.post('/api/token/', data={'email': special_reseller.email, 'password': 'secure-password'})
    return response.data


@pytest.fixture
def auth_api_client(api_client, reseller_token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reseller_token['access']}")
    return api_client


@pytest.fixture
def auth_api_client_special_reseller(api_client, special_reseller_token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {special_reseller_token['access']}")
    return api_client


@pytest.fixture
def purchase(reseller):
    return baker.make('purchase.Purchase', reseller_cpf=reseller)
