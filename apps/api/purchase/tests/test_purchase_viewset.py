import unittest

import pytest
from django.conf import settings
from model_bakery import baker

from apps.api.purchase.models import Purchase


@pytest.fixture
def purchase_data():
    data = {
        'code': 'abc-123',
        'value': 1000.00,
        'purchase_date': '2021-12-01',
    }
    return data


@pytest.mark.django_db
class TestPurchaseViewSet:
    def test_retrieve_purchase_with_success(self, auth_api_client, purchase):
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

    def test_list_resellers_purchases_with_success(self, auth_api_client, reseller):
        baker.make('purchase.Purchase', reseller_cpf=reseller, _quantity=5)

        # Create more 15 purchases of others resellers
        for _ in range(3):
            other_resellers = baker.make('reseller.Reseller')
            baker.make('purchase.Purchase', reseller_cpf=other_resellers, _quantity=5)

        response = auth_api_client.get('/api/purchase/')

        assert 200 == response.status_code
        assert 5 == len(response.data)

        purchases = Purchase.objects.filter(reseller_cpf=reseller)

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

    def test_create_pre_approved_purchase_with_success(self, auth_api_client_special_reseller, purchase_data):
        response = auth_api_client_special_reseller.post('/api/purchase/', data=purchase_data)

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

    @pytest.mark.parametrize(('value', 'expected'), [(1000, 10.0), (1001, 15.0), (1500, 15.0), (1501, 20.0)])
    def test_get_cashback_percentage(self, value, expected, auth_api_client, purchase_data, purchase):
        purchase.value = value
        purchase.save()

        assert expected == purchase.get_cashback_percentage()

    @pytest.mark.parametrize(('value', 'expected'), [(1000, 100.0), (1001, 150.15), (1500, 225.0), (1501, 300.2)])
    def test_get_cashback_value(self, value, expected, auth_api_client, purchase_data, purchase):
        purchase.value = value
        purchase.save()

        assert expected == purchase.get_cashback_value()

    @pytest.mark.parametrize('method', ['put', 'patch'])
    def test_edit_purchase_with_success(self, method, auth_api_client, purchase_data, purchase):
        response = getattr(auth_api_client, method)(f'/api/purchase/{purchase.purchase_uuid}/',
                                                    data={**purchase_data, 'value': 2000.00})

        assert 200 == response.status_code

        assert response.json() == {
            'purchase_uuid': str(purchase.purchase_uuid),
            'cpf': '109.876.543-21',
            'code': 'abc-123',
            'value': 2000.00,
            'purchase_date': '2021-12-01',
            'cashback_percentage': 20.0,
            'cashback_value': 400.00,
            'status': 'validating'
        }

    @pytest.mark.parametrize('method', ['put', 'patch'])
    @pytest.mark.parametrize('status', ['approved', 'reproved'])
    def test_cannot_edit_purchase_if_status_is_not_validating(self, method, status, auth_api_client, purchase_data,
                                                              reseller):
        purchase = baker.make('purchase.Purchase', reseller_cpf=reseller, status=status)

        response = getattr(auth_api_client, method)(f'/api/purchase/{purchase.purchase_uuid}/',
                                                    data={**purchase_data, 'value': 2000.00})

        assert 403 == response.status_code

    def test_delete_purchase_with_success(self, auth_api_client, purchase):
        response = auth_api_client.delete(f'/api/purchase/{purchase.purchase_uuid}/')

        assert 204 == response.status_code

    @pytest.mark.parametrize('status', ['approved', 'reproved'])
    def test_cannot_delete_purchase_if_status_is_not_validating(self, status, auth_api_client, purchase_data, reseller):
        purchase = baker.make('purchase.Purchase', reseller_cpf=reseller, status=status)

        response = auth_api_client.delete(f'/api/purchase/{purchase.purchase_uuid}/')

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
