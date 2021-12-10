import pytest


@pytest.fixture
def reseller_data():
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'cpf': '333.257.650-09',
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
            'cpf': '333.257.650-09',
            'email': 'john.doe@email.com'
        }

    @pytest.mark.parametrize('invalid_cpf', ['using-letters', '111.111.111-11', '123321123321123',
                                             '333^257.650c09', '333~257.650-00', '333.257.650-00'])
    def test_create_reseller_failed_for_invalid_cpf(self, invalid_cpf, api_client, reseller_data):
        reseller_data = {**reseller_data, 'cpf': invalid_cpf}
        response = api_client.post('/api/reseller/', data=reseller_data)

        assert 400 == response.status_code
        assert response.json() == {'cpf': ['Invalid CPF']}

    @pytest.mark.parametrize('field', ['first_name', 'last_name', 'cpf', 'email', 'password'])
    def test_create_reseller_failed_without_required_fields(self, field, api_client, reseller_data):
        del reseller_data[field]
        response = api_client.post('/api/reseller/', data=reseller_data)

        assert 400 == response.status_code
        assert response.json() == {field: ['This field is required.']}


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
