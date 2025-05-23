from typing import Any, Dict

from fastapi import WebSocket


class GlobalConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int) -> None:
        self.active_connections.pop(user_id, None)

    def has_connection(self, user_id: int) -> bool:
        return user_id in self.active_connections

    async def send_personal_message(
        self, user_id: int, message: dict[str, Any]
    ) -> None:
        ws = self.active_connections.get(user_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, user_ids: list[int], message: dict[str, Any]) -> None:
        for uid in user_ids:
            await self.send_personal_message(uid, message)


manager: GlobalConnectionManager = GlobalConnectionManager()
