from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src import get_db, get_redis
from src.auth import get_current_user_ws
from src.core import User
from src.rooms.service import get_room_user_ids

from src.messages.service import (
    send_message,
    get_messages_by_room,
    get_message_by_id,
    update_message,
    delete_message,
)
from src.messages.schemas import (
    MessageCreate,
    MessageUpdate,
)
from src.messages.manager import manager

router = APIRouter(prefix="/ws/chat", tags=["chat websocket"])


@router.websocket("/{room_id}")
async def chat_ws(
        websocket: WebSocket,
        room_id: int,
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
        current_user: User = Depends(get_current_user_ws)
):
    await manager.connect(current_user.id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            match action:
                case "send_message":
                    payload = MessageCreate(**data["data"])
                    result = await send_message(payload, db, redis, current_user)
                    await manager.broadcast_to_room(
                        user_ids=await get_room_user_ids(room_id, db),
                        message={"type": "new_message", "data": result}
                    )

                case "get_messages":
                    messages = await get_messages_by_room(room_id, db, current_user)
                    await websocket.send_json({
                        "type": "message_history",
                        "data": [m.to_dict() for m in messages]
                    })

                case "get_message":
                    msg_id = data["message_id"]
                    message = await get_message_by_id(msg_id, db, current_user)
                    if message:
                        await websocket.send_json({
                            "type": "message_detail",
                            "data": message.to_dict()
                        })

                case "edit_message":
                    payload = MessageUpdate(**data["data"])
                    result = await update_message(payload, db, current_user)
                    await manager.broadcast_to_room(
                        user_ids=await get_room_user_ids(room_id, db),
                        message={"type": "message_edited", "data": result}
                    )

                case "delete_message":
                    msg_id = data["message_id"]
                    result = await delete_message(msg_id, db, current_user)
                    await manager.broadcast_to_room(
                        user_ids=await get_room_user_ids(room_id, db),
                        message={"type": "message_deleted", "data": result}
                    )

    except WebSocketDisconnect:
        manager.disconnect(current_user.id)
