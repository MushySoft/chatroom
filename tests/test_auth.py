from tests.conftest import get_client
from tests.fixtures.oauth import patch_google_oauth


def test_login_redirect():
    client = get_client()
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert response.json() == {"redirect": "https://google.com/redirect"}


def test_auth_callback_success():
    client = get_client()
    response = client.get("/auth/callback")
    assert response.status_code == 200
    assert response.json()["access_token"] == "mock_token"
    assert response.json()["user"]["username"] == "TestUser"


def test_logout():
    client = get_client()
    headers = {"Authorization": "Bearer mock_access_token"}
    response = client.get("/auth/logout", headers=headers)
    assert response.status_code == 204
