import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestHealthCheck:
    def test_health_check_endpoint_works(self, client):
        response = client.get(reverse("health-check"))
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["service"] == "bookstore"
