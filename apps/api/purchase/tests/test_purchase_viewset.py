import unittest

import pytest
from django.conf import settings
from model_bakery import baker

from apps.api.purchase.models import Purchase


@pytest.fixture
def purchase_data():
    data = {
        'cpf': '109.876.543-21',
        'code': 'abc-123',
        'value': 1000.00,
        'purchase_date': '2021-12-01',
    }
    return data


@pytest.mark.django_db
class TestPurchaseViewSet:
    def test_retrieve_purchase_with_success(self, auth_api_client):
        reseller = baker.make('reseller.Reseller')
        purchase = baker.make('purchase.Purchase', reseller_cpf=reseller)

        response = auth_api_client.get(f'/api/purchase/{str(purchase.purchase_uuid)}', follow=True)

        assert 200 == response.status_code

        assert response.data == {
            'purchase_uuid': str(purchase.purchase_uuid),
            'cpf': purchase.reseller_cpf.cpf,
            'code': purchase.code,
            'value': float(purchase.value),
            'purchase_date': str(purchase.purchase_date),
            'cashback_percentage': purchase.get_cashback_percentage(),
            'cashback_value': purchase.get_cashback_value(),
            'status': purchase.status
        }

    def test_list_purchase_with_success(self, auth_api_client):
        for _ in range(10):
            reseller = baker.make('reseller.Reseller')
            baker.make('purchase.Purchase', reseller_cpf=reseller)

        response = auth_api_client.get('/api/purchase/')

        assert 200 == response.status_code
        assert 10 == len(response.data)

        purchases = Purchase.objects.all()

        case = unittest.TestCase()
        case.assertCountEqual(response.data, [
            {
                'purchase_uuid': str(purchase.purchase_uuid),
                'cpf': purchase.reseller_cpf.cpf,
                'code': purchase.code,
                'value': float(purchase.value),
                'purchase_date': str(purchase.purchase_date),
                'cashback_percentage': purchase.get_cashback_percentage(),
                'cashback_value': purchase.get_cashback_value(),
                'status': purchase.status
            }
            for purchase in purchases
        ])

    def test_create_new_purchase_with_success(self, auth_api_client, purchase_data):
        response = auth_api_client.post('/api/purchase/', data=purchase_data)

        assert 201 == response.status_code

        assert response.json() == {
            'purchase_uuid': response.data['purchase_uuid'],
            'cpf': '109.876.543-21',
            'code': 'abc-123',
            'value': 1000.00,
            'purchase_date': '2021-12-01',
            'cashback_percentage': 10.0,
            'cashback_value': 100.00,
            'status': 'validating'
        }

    def test_create_pre_approved_purchase_with_success(self, auth_api_client, purchase_data):
        purchase_data = {**purchase_data, 'cpf': '153.509.460-56'}
        response = auth_api_client.post('/api/purchase/', data=purchase_data)

        assert 201 == response.status_code

        assert response.json() == {
            'purchase_uuid': response.data['purchase_uuid'],
            'cpf': '153.509.460-56',
            'code': 'abc-123',
            'value': 1000.00,
            'purchase_date': '2021-12-01',
            'cashback_percentage': 10.0,
            'cashback_value': 100.00,
            'status': 'approved'
        }

    @pytest.mark.parametrize('method', ['put', 'patch'])
    def test_edit_purchase_with_success(self, method, auth_api_client, purchase_data):
        purchase_resp = auth_api_client.post('/api/purchase/', data=purchase_data)

        response = getattr(auth_api_client, method)(f'/api/purchase/{purchase_resp.data["purchase_uuid"]}/',
                                                    data={**purchase_data, 'value': 2000.00})

        assert 200 == response.status_code

        assert response.json() == {
            'purchase_uuid': purchase_resp.data['purchase_uuid'],
            'cpf': '109.876.543-21',
            'code': 'abc-123',
            'value': 2000.00,
            'purchase_date': '2021-12-01',
            'cashback_percentage': 20.0,
            'cashback_value': 400.00,
            'status': 'validating'
        }

    @pytest.mark.parametrize('method', ['put', 'patch'])
    def test_cannot_edit_purchase_if_status_is_not_validating(self, method, auth_api_client, purchase_data):
        purchase_data = {**purchase_data, 'cpf': '153.509.460-56'}
        purchase_resp = auth_api_client.post('/api/purchase/', data=purchase_data)

        response = getattr(auth_api_client, method)(f'/api/purchase/{purchase_resp.data["purchase_uuid"]}/',
                                                    data={**purchase_data, 'value': 2000.00})

        assert 403 == response.status_code

    def test_delete_purchase_with_success(self, auth_api_client, purchase_data):
        purchase_resp = auth_api_client.post('/api/purchase/', data=purchase_data)

        response = auth_api_client.delete(f'/api/purchase/{purchase_resp.data["purchase_uuid"]}/')

        assert 204 == response.status_code

    def test_cannot_delete_purchase_if_status_is_not_validating(self, auth_api_client, purchase_data):
        purchase_data = {**purchase_data, 'cpf': '153.509.460-56'}
        purchase_resp = auth_api_client.post('/api/purchase/', data=purchase_data)

        response = auth_api_client.delete(f'/api/purchase/{purchase_resp.data["purchase_uuid"]}/')

        assert 403 == response.status_code

    def test_retrieve_cashback_with_success(self, requests_mock, auth_api_client):
        json_data = {"statusCode": 200, "body": {"credit": 3600}}
        requests_mock.get(settings.CASHBACK_API_URL, json=json_data)

        response = auth_api_client.get(f'/api/purchase/cashback/', follow=True)

        assert 200 == response.status_code
        assert response.data == {'credit': 3600}

    def test_retrieve_cashback_error_message(self, requests_mock, auth_api_client):
        json_data = {"statusCode": 400,
                     "body": {"message": "CPF do revendedor(a) está incorreto, utilize apenas números!"}}
        requests_mock.get(settings.CASHBACK_API_URL, json=json_data)

        response = auth_api_client.get(f'/api/purchase/cashback/', follow=True)

        assert 400 == response.status_code
        assert response.data == {'message': 'CPF do revendedor(a) está incorreto, utilize apenas números!'}
