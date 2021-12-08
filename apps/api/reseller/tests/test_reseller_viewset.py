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
        response = api_client.post('/api/reseller/', data=reseller_data)

        assert 201 == response.status_code

        assert response.json() == {
            'first_name': 'John',
            'last_name': 'Doe',
            'cpf': '123.456.789-10',
            'email': 'john.doe@email.com'
        }

    @pytest.mark.parametrize('field', ['first_name', 'last_name', 'cpf', 'email', 'password'])
    def test_create_reseller_failed_without_required_fields(self, field, api_client, reseller_data):
        del reseller_data[field]
        response = api_client.post('/api/reseller/', data=reseller_data)

        assert 400 == response.status_code


@pytest.mark.django_db
class TestResellerLogin:
    def test_get_reseller_get_token_with_success(self, api_client, reseller_data):
        api_client.post('/api/reseller/', data=reseller_data)
        response = api_client.post('/api/token/', data={'email': 'john.doe@email.com', 'password': 'secure-password'})

        assert 200 == response.status_code

        response_data = response.json()
        assert 'access' in response_data.keys()
        assert 'refresh' in response_data.keys()

    def test_use_refresh_reseller_token_with_success(self, api_client, reseller_data):
        api_client.post('/api/reseller/', data=reseller_data)
        resp_token = api_client.post('/api/token/', data={'email': 'john.doe@email.com', 'password': 'secure-password'})
        resp_token = resp_token.json()

        response = api_client.post('/api/token/refresh/', data={'refresh': resp_token['refresh']})

        assert 200 == response.status_code

        assert response.data['access'] != resp_token['access']
