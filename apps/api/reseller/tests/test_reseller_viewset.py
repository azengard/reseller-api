import pytest


@pytest.fixture
def reseller_data():
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'cpf': '123.456.789-10',
        'email': 'john.doe@email.com',
        'password': 'secure-password'
    }
    return data


@pytest.mark.django_db
class TestResellerViewSet:
    def test_create_reseller_with_success(self, api_client, reseller_data):
        response = api_client.post('/api/v1/reseller/', data=reseller_data)

        assert 201 == response.status_code
        assert response.json() == reseller_data

    @pytest.mark.parametrize('field', ['first_name', 'last_name', 'cpf', 'email', 'password'])
    def test_create_reseller_failed_without_required_fields(self, field, api_client, reseller_data):
        del reseller_data[field]
        response = api_client.post('/api/v1/reseller/', data=reseller_data)

        assert 400 == response.status_code
