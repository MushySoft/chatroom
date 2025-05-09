import time
from unittest.mock import AsyncMock

from src import Pagination
from src.messages.manager import manager as chat_manager
from src.websocket.manager import manager as global_manager
from tests.conftest import get_client


def test_global_websocket_get_room_list():
    client = get_client(for_ws=True)
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json({"action": "get_room_list"})
        data = websocket.receive_json()

        assert data["type"] == "room_list"
        assert isinstance(data["data"], list)
        assert data["data"][0]["id"] == 1
        assert data["data"][0]["name"] == "Test Room"
        assert data["data"][0]["last_message"]["content"] == "Hello!"

        assert global_manager.has_connection(1)

        websocket.close()
        time.sleep(0.1)
        assert not global_manager.has_connection(1)


def test_chat_ws_get_messages():
    client = get_client(for_ws=True)

    with client.websocket_connect("/ws/chat/1") as websocket:
        websocket.send_json(
            {"action": "get_messages", "pagination": {"limit": 5, "offset": 0}}
        )
        response = websocket.receive_json()

        assert response["type"] == "message_history"
        assert isinstance(response["data"], list)
        assert response["data"][0]["content"] == "Hello!"
        assert response["data"][0]["sender_id"] == 1

        assert chat_manager.active_connections.get(1) is not None

        websocket.close()
        time.sleep(0.1)
        assert chat_manager.active_connections.get(1) is None


def test_chat_ws_get_message():
    client = get_client(for_ws=True)

    with client.websocket_connect("/ws/chat/1") as websocket:
        websocket.send_json({"action": "get_message", "message_id": 1})
        response = websocket.receive_json()

        assert response["type"] == "message_detail"
        assert response["data"]["id"] == 1
        assert response["data"]["content"] == "Hello!"
        assert response["data"]["sender_id"] == 1

        websocket.close()
        time.sleep(0.1)


def test_chat_ws_send_message(monkeypatch):
    client = get_client(for_ws=True)

    with client.websocket_connect("/ws/chat/1") as websocket:
        websocket.send_json(
            {
                "action": "send_message",
                "data": {"room_id": 1, "content": "New test message", "files": []},
            }
        )

        response = websocket.receive_json()

        assert response["type"] == "new_message"
        assert response["data"]["room_id"] == 1
        assert response["data"]["content"] == "New test message"
        assert response["data"]["sender_id"] == 1

        websocket.close()
        time.sleep(0.1)


def test_chat_ws_edit_message(monkeypatch):
    client = get_client(for_ws=True)

    with client.websocket_connect("/ws/chat/1") as websocket:
        websocket.send_json(
            {
                "action": "edit_message",
                "data": {"message_id": 1, "content": "Edited message"},
            }
        )

        response = websocket.receive_json()

        assert response["type"] == "message_edited"
        assert response["data"]["message_id"] == 1
        assert response["data"]["status"] == "updated"

        websocket.close()
        time.sleep(0.1)


def test_chat_ws_delete_message(monkeypatch):
    client = get_client(for_ws=True)

    with client.websocket_connect("/ws/chat/1") as websocket:
        websocket.send_json({"action": "delete_message", "message_id": 1})

        response = websocket.receive_json()

        assert response["type"] == "message_deleted"
        assert response["data"]["message_id"] == 1

        websocket.close()
        time.sleep(0.1)
