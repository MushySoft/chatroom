from redis.asyncio import Redis
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_temp_files, clear_temp_files
from src.core.models import User, Message, FileStorage

from src.message.schemas import MessageCreate


async def send_message(
        data: MessageCreate,
        db: AsyncSession,
        redis: Redis,
        current_user: User
):
    new_msg = Message(
        room_id=data.room_id,
        sender_id=current_user.id,
        content=data.content,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(new_msg)
    await db.flush()

    files = await get_temp_files(redis, current_user.id)
    for file in files:
        db.add(FileStorage(message_id=new_msg.id, file_url=file["url"]))

    await db.commit()
    await clear_temp_files(redis, current_user.id)

    return {"message_id": new_msg.id}
