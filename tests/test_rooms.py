from tests.conftest import get_client


def test_create_room():
    client = get_client()
    response = client.post("/rooms/", json={"name": "test room", "is_private": False})
    assert response.status_code == 201
    assert response.json()["name"] == "test room"


def test_invite_user():
    client = get_client()
    response = client.post("/rooms/invite", json={"room_id": 1, "receiver_id": 2})
    assert response.status_code == 201
    assert "invitation_id" in response.json()


def test_get_sent_invitations():
    client = get_client()
    response = client.get("/rooms/invitations/sent")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_received_invitations():
    client = get_client()
    response = client.get("/rooms/invitations/received")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_respond_to_invite():
    client = get_client(active_user=2)
    response = client.post(
        "/rooms/invitations/respond", json={"invitation_id": 1, "accept": True}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_remove_user_from_room():
    client = get_client()
    response = client.delete("/rooms/1/users/2")
    assert response.status_code == 200


def test_leave_room():
    client = get_client()
    response = client.delete("/rooms/1/leave")
    assert response.status_code == 200


def test_get_room_participants():
    client = get_client()
    response = client.get("/rooms/1/participants")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_all_rooms():
    client = get_client()
    response = client.get("/rooms/all")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_patch_room():
    client = get_client()
    response = client.patch("/rooms/1", json={"name": "updated", "is_private": False})
    assert response.status_code == 200


def test_search_rooms():
    client = get_client()
    response = client.get("/rooms/search", params={"text": "test"})
    assert response.status_code == 200
    rooms = response.json()
    assert isinstance(rooms, list)
    for room in rooms:
        assert "name" in room


def test_join_public_room():
    client = get_client()
    response = client.post("/rooms/join/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["is_private"] is False
