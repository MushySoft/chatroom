from typing import Any, Dict

from fastapi import WebSocket


class ChatConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[int, WebSocket] = {}
        self.user_rooms: Dict[int, int] = {}

    async def connect(self, user_id: int, websocket: WebSocket, room_id: int) -> None:
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_rooms[user_id] = room_id

    def disconnect(self, user_id: int) -> None:
        self.active_connections.pop(user_id, None)
        self.user_rooms.pop(user_id, None)

    async def send_personal_message(
        self, user_id: int, message: dict[str, Any]
    ) -> None:
        ws = self.active_connections.get(user_id)
        if ws:
            await ws.send_json(message)

    async def broadcast_to_room(
        self, user_ids: list[int], message: dict[str, Any]
    ) -> None:
        for uid in user_ids:
            await self.send_personal_message(uid, message)

    def get_online_rooms(self) -> set[int]:
        return set(self.user_rooms.values())

    def get_online_users_in_room(self, room_id: int) -> list[int]:
        return [uid for uid, rid in self.user_rooms.items() if rid == room_id]


manager: ChatConnectionManager = ChatConnectionManager()
