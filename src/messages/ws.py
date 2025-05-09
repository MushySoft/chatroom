from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src import Pagination, get_db, get_redis
from src.auth import get_current_user_ws
from src.core import User
from src.messages.manager import manager
from src.messages.schemas import (
    MessageCreateRequest,
    MessageUpdateRequest,
)
from src.messages.service import (
    delete_message,
    get_message_by_id,
    get_messages_by_room,
    send_message,
    update_message,
)

router = APIRouter(prefix="/ws/chat", tags=["chat websocket"])


@router.websocket("/{room_id}")
async def chat_ws(  # type: ignore[no-untyped-def]
    websocket: WebSocket,
    room_id: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user_ws),
):
    await manager.connect(current_user.id, websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            match action:
                case "send_message":
                    payload_create = MessageCreateRequest(**data["data"])
                    result_send = await send_message(
                        payload_create, db, redis, current_user
                    )
                    online_users = manager.get_online_users_in_room(room_id)
                    await manager.broadcast_to_room(
                        user_ids=online_users,
                        message={
                            "type": "new_message",
                            "data": result_send.model_dump(mode="json"),
                        },
                    )

                case "get_messages":
                    pagination_data = data.get("pagination")
                    pagination = (
                        Pagination(**pagination_data)
                        if pagination_data
                        else Pagination()
                    )

                    messages = await get_messages_by_room(
                        room_id, db, current_user, pagination=pagination
                    )
                    await websocket.send_json(
                        {
                            "type": "message_history",
                            "data": [m.model_dump(mode="json") for m in messages],
                        }
                    )

                case "get_message":
                    msg_id = data["message_id"]
                    message = await get_message_by_id(msg_id, db, current_user)
                    if message:
                        await websocket.send_json(
                            {
                                "type": "message_detail",
                                "data": message.model_dump(mode="json"),
                            }
                        )

                case "edit_message":
                    payload_update = MessageUpdateRequest(**data["data"])
                    result_edit = await update_message(payload_update, db, current_user)
                    online_users = manager.get_online_users_in_room(room_id)
                    await manager.broadcast_to_room(
                        user_ids=online_users,
                        message={
                            "type": "message_edited",
                            "data": result_edit.model_dump(mode="json"),
                        },
                    )

                case "delete_message":
                    msg_id = data["message_id"]
                    result_delete = await delete_message(msg_id, db, current_user)
                    online_users = manager.get_online_users_in_room(room_id)
                    await manager.broadcast_to_room(
                        user_ids=online_users,
                        message={
                            "type": "message_deleted",
                            "data": result_delete.model_dump(mode="json"),
                        },
                    )

    except WebSocketDisconnect:
        manager.disconnect(current_user.id)
