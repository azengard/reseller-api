import pytest
from rest_framework.test import APIClient


@pytest.fixture()
def api_client():
    api_client = APIClient()
    return api_client
