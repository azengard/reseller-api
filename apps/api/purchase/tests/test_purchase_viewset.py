import pytest


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
    def test_create_new_purchase_with_success(self, auth_api_client, purchase_data):
        response = auth_api_client.post('/api/purchase/', data=purchase_data)

        assert 201 == response.status_code

        assert response.json() == {
            'cpf': '109.876.543-21',
            'code': 'abc-123',
            'value': 1000.00,
            'purchase_date': '2021-12-01',
            'status': 'validating'
        }

    def test_create_pre_approved_purchase_with_success(self, auth_api_client, purchase_data):
        purchase_data = {**purchase_data, 'cpf': '153.509.460-56'}
        response = auth_api_client.post('/api/purchase/', data=purchase_data)

        assert 201 == response.status_code

        assert response.json() == {
            'cpf': '153.509.460-56',
            'code': 'abc-123',
            'value': 1000.00,
            'purchase_date': '2021-12-01',
            'status': 'approved'
        }
