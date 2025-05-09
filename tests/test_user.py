from tests.conftest import get_client


def test_get_me():
    client = get_client()
    response = client.get("/user/me", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "TestUser"
    assert data["email"] == "test@example.com"


def test_patch_username():
    client = get_client()
    payload = {"username": "NewName"}
    response = client.patch(
        "/user/username", headers={"Authorization": "Bearer mock_token"}, json=payload
    )
    assert response.status_code == 200
    assert response.json()["new_username"] == "NewName"


def test_get_user_by_id():
    client = get_client()
    response = client.get("/user/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


# noinspection PyTypeChecker
def test_search_users():
    client = get_client()
    response = client.get("/user/search?username=test")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert users[0]["username"] == "TestUser"
