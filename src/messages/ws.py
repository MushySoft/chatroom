from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_db, get_redis
from src.auth import get_current_user_ws
from src.core import User
from src.messages.manager import manager
from src.messages.schemas import (
    MessageCreate,
    MessageUpdate,
)
from src.messages.service import (
    delete_message,
    get_message_by_id,
    get_messages_by_room,
    send_message,
    update_message,
)
from src.rooms.service import get_room_user_ids

router = APIRouter(prefix="/ws/chat", tags=["chat websocket"])


@router.websocket("/{room_id}")
async def chat_ws(  # type: ignore[no-untyped-def]
    websocket: WebSocket,
    room_id: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user_ws),
):
    await manager.connect(current_user.id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            match action:
                case "send_message":
                    payload_create = MessageCreate(**data["data"])
                    result_send = await send_message(
                        payload_create, db, redis, current_user
                    )
                    await manager.broadcast_to_room(
                        user_ids=await get_room_user_ids(room_id, db),
                        message={"type": "new_message", "data": result_send},
                    )

                case "get_messages":
                    messages = await get_messages_by_room(
                        room_id, db, current_user, pagination=data.get("pagination")
                    )
                    await websocket.send_json(
                        {
                            "type": "message_history",
                            "data": [m for m in messages],
                        }
                    )

                case "get_message":
                    msg_id = data["message_id"]
                    message = await get_message_by_id(msg_id, db, current_user)
                    if message:
                        await websocket.send_json(
                            {"type": "message_detail", "data": message}
                        )

                case "edit_message":
                    payload_update = MessageUpdate(**data["data"])
                    result_edit = await update_message(payload_update, db, current_user)
                    await manager.broadcast_to_room(
                        user_ids=await get_room_user_ids(room_id, db),
                        message={"type": "message_edited", "data": result_edit},
                    )

                case "delete_message":
                    msg_id = data["message_id"]
                    result_delete = await delete_message(msg_id, db, current_user)
                    await manager.broadcast_to_room(
                        user_ids=await get_room_user_ids(room_id, db),
                        message={"type": "message_deleted", "data": result_delete},
                    )

    except WebSocketDisconnect:
        manager.disconnect(current_user.id)
