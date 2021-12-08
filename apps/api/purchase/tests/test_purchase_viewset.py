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
            'purchase_uuid': response.data['purchase_uuid'],
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
            'purchase_uuid': response.data['purchase_uuid'],
            'cpf': '153.509.460-56',
            'code': 'abc-123',
            'value': 1000.00,
            'purchase_date': '2021-12-01',
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
            'status': 'validating'
        }
