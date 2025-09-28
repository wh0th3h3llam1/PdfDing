import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api_auth.models import AccessToken

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestAccessTokenViews:
    def test_permissions_required(self, api_client):
        url = reverse("api_tokens-list")
        api_client.logout()
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_creation(self, api_client):
        url = reverse("api_tokens-list")
        data = {"name": "createdtoken"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data
        assert response.data["name"] == "createdtoken"

    def test_token_deletion(self, api_client, token):
        url = reverse("api_tokens-detail", args=[token.id])
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not AccessToken.objects.filter(id=token.id).exists()

    def test_token_rotation(self, api_client, token):
        url = reverse("api_tokens-rotate", args=[token.id])
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data
        assert response.data["id"] != token.id
        assert AccessToken.objects.filter(id=response.data["id"]).exists()
