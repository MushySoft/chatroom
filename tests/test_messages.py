from tests.conftest import get_client


def test_send_message():
    client = get_client()
    response = client.post("/messages/", json={"room_id": 1, "content": "Hello!"})
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Hello!"
    assert data["room_id"] == 1
    assert "created_at" in data


def test_get_messages_by_room():
    client = get_client()
    response = client.get("/messages/room/1")
    assert response.status_code == 200
    messages = response.json()
    assert isinstance(messages, list)


def test_get_message_by_id():
    client = get_client()
    response = client.get("/messages/1")
    assert response.status_code == 200
    message = response.json()
    assert message["id"] == 1
    assert message["room_id"] == 1


def test_update_message():
    client = get_client()
    payload = {
        "message_id": 1,
        "new_content": "Updated message",
        "file_urls": ["https://test/file1.jpg"],
    }
    response = client.patch("/messages/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message_id"] == 1
    assert data["status"] == "updated"


def test_delete_message():
    client = get_client()
    response = client.delete("/messages/1")
    assert response.status_code == 200
    data = response.json()
    assert data["message_id"] == 1
    assert data["status"] == "deleted"


def test_search_messages_in_room():
    client = get_client()

    search_resp = client.get("/messages/search/hello", params={"room_id": 1})
    assert search_resp.status_code == 200
    messages = search_resp.json()
    assert isinstance(messages, list)
    assert any("hello" in msg["content"].lower() for msg in messages)
