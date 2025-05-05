from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis

from src import get_db, get_redis
from src.auth import get_current_user_ws
from src.core import User, Room, RoomUser, Message

from src.websocket.manager import manager
from src.websocket.service import set_user_active, set_user_offline

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("")
async def global_ws(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user_ws),
):
    await manager.connect(current_user.id, websocket)
    await set_user_active(current_user.id, db)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            match action:
                case "get_room_list":
                    result = await db.execute(
                        select(Room)
                        .join(RoomUser)
                        .where(RoomUser.user_id == current_user.id)
                    )
                    rooms = result.scalars().all()
                    room_data = []

                    for room in rooms:
                        msg_result = await db.execute(
                            select(Message)
                            .where(Message.room_id == room.id)
                            .order_by(Message.created_at.desc())
                            .limit(1)
                        )
                        last_msg = msg_result.scalar_one_or_none()
                        room_data.append(
                            {
                                "id": room.id,
                                "name": room.name,
                                "last_message": (
                                    {
                                        "id": last_msg.id,
                                        "content": last_msg.content,
                                        "created_at": last_msg.created_at.isoformat(),
                                        "sender_id": last_msg.sender_id,
                                    }
                                    if last_msg
                                    else None
                                ),
                            }
                        )

                    await websocket.send_json({"type": "room_list", "data": room_data})

    except WebSocketDisconnect:
        manager.disconnect(current_user.id)
        await set_user_offline(current_user.id, db)
