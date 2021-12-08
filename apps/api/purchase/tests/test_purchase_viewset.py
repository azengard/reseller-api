import unittest

import pytest
from model_bakery import baker


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
            'cashback_percentage': 'cashback_percentage',
            'cashback_value': 'cashback_value',
            'status': purchase.status
        }

    def test_list_purchase_with_success(self, auth_api_client):
        purchases = []
        for _ in range(10):
            reseller = baker.make('reseller.Reseller')
            purchases.append(baker.make('purchase.Purchase', reseller_cpf=reseller))

        response = auth_api_client.get('/api/purchase/')

        assert 200 == response.status_code
        assert 10 == len(response.data)

        case = unittest.TestCase()
        case.assertCountEqual(response.data, [
            {
                'purchase_uuid': str(purchase.purchase_uuid),
                'cpf': purchase.reseller_cpf.cpf,
                'code': purchase.code,
                'value': float(purchase.value),
                'purchase_date': str(purchase.purchase_date),
                'cashback_percentage': 'cashback_percentage',
                'cashback_value': 'cashback_value',
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
            'cashback_percentage': 'cashback_percentage',
            'cashback_value': 'cashback_value',
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
            'cashback_percentage': 'cashback_percentage',
            'cashback_value': 'cashback_value',
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
            'cashback_percentage': 'cashback_percentage',
            'cashback_value': 'cashback_value',
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
