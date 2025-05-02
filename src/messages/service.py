from redis.asyncio import Redis
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

from src import get_temp_files, clear_temp_files, Pagination
from src.core.models import User, Message, FileStorage, MessageStatus, RoomUser

from src.messages.schemas import MessageCreate, MessageUpdate


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

    participants_result = await db.execute(
        select(RoomUser.user_id)
        .where(RoomUser.room_id == data.room_id)
    )
    participant_ids = participants_result.scalars().all()

    for user_id in participant_ids:
        status_value = "sent" if user_id == current_user.id else "delivered"
        db.add(MessageStatus(
            message_id=new_msg.id,
            user_id=user_id,
            status=status_value,
            updated_at=datetime.now()
        ))

    files = await get_temp_files(redis, current_user.id)
    for file in files:
        db.add(FileStorage(message_id=new_msg.id, file_url=file["url"]))

    await db.commit()
    await clear_temp_files(redis, current_user.id)

    return {"message_id": new_msg.id}


async def get_message_by_id(
        message_id: int,
        db: AsyncSession,
        current_user: User
):
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.files))
        .join(MessageStatus)
        .where(
            Message.id == message_id,
            MessageStatus.user_id == current_user.id,
            MessageStatus.status.in_(["delivered", "viewed"])
        )
    )
    message = result.scalar_one_or_none()

    if not message:
        return None

    await db.execute(
        update(MessageStatus)
        .where(
            MessageStatus.message_id == message.id,
            MessageStatus.user_id == current_user.id
        )
        .values(status="viewed", updated_at=datetime.now())
    )
    await db.commit()
    return message


async def get_messages_by_room(
        room_id: int,
        db: AsyncSession,
        current_user: User,
        pagination: Pagination,
):
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.files))
        .join(MessageStatus)
        .where(
            Message.room_id == room_id,
            MessageStatus.user_id == current_user.id,
            MessageStatus.status.in_(["delivered", "viewed"])
        )
        .order_by(Message.created_at)
        .limit(pagination.limit)
        .offset(pagination.offset)
    )
    messages = result.scalars().all()

    await db.execute(
        update(MessageStatus)
        .where(
            MessageStatus.message_id.in_([m.id for m in messages]),
            MessageStatus.user_id == current_user.id
        )
        .values(status="viewed", updated_at=datetime.now())
    )
    await db.commit()

    return messages


async def update_message(
        data: MessageUpdate,
        db: AsyncSession,
        current_user: User
):
    result = await db.execute(
        select(Message)
        .where(Message.id == data.message_id)
        .options(selectinload(Message.files))
    )
    message = result.scalar_one_or_none()

    if not message:
        raise ValueError("Message not found")

    if message.sender_id != current_user.id:
        raise PermissionError("You can only edit your own messages")

    if data.new_content is not None:
        message.content = data.new_content

    message.updated_at = datetime.now()

    await db.execute(
        delete(FileStorage).where(FileStorage.message_id == message.id)
    )

    for url in data.file_urls:
        db.add(FileStorage(message_id=message.id, file_url=url))

    await db.execute(
        update(MessageStatus)
        .where(
            MessageStatus.message_id == message.id,
            MessageStatus.user_id != current_user.id,
            MessageStatus.status != "deleted"
        )
        .values(status="delivered", updated_at=datetime.now())
    )

    await db.commit()

    return {"message_id": message.id, "status": "updated"}


async def delete_message(
        message_id: int,
        db: AsyncSession,
        current_user: User
):
    await db.execute(
        update(MessageStatus)
        .where(
            MessageStatus.message_id == message_id,
            MessageStatus.user_id == current_user.id
        )
        .values(status="deleted", updated_at=datetime.now())
    )
    await db.commit()
    return {"message_id": message_id, "status": "deleted"}
