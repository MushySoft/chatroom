import datetime
from typing import List, Optional

from redis.asyncio import Redis
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src import Pagination, clear_temp_files, get_temp_files
from src.core import FileStorage, Message, MessageStatus, RoomUser, User
from src.messages.schemas import (
    MessageCreateRequest,
    MessageCreateResponse,
    MessageDeleteResponse,
    MessagePublic,
    MessageSender,
    MessageUpdateRequest,
    MessageUpdateResponse,
)


async def send_message(
    data: MessageCreateRequest, db: AsyncSession, redis: Redis, current_user: User
) -> MessageCreateResponse:
    new_msg = Message(
        room_id=data.room_id,
        sender_id=current_user.id,
        content=data.content,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    db.add(new_msg)
    await db.flush()

    participants_result = await db.execute(
        select(RoomUser.user_id).where(RoomUser.room_id == data.room_id)
    )
    participant_ids = participants_result.scalars().all()

    for user_id in participant_ids:
        status_value = "delivered"
        db.add(
            MessageStatus(
                message_id=new_msg.id,
                user_id=user_id,
                status=status_value,
                updated_at=datetime.datetime.now(),
            )
        )

    files = await get_temp_files(redis, current_user.id, room_id=data.room_id)
    for file in files:
        db.add(FileStorage(message_id=new_msg.id, file_url=file["url"]))

    await db.commit()
    await clear_temp_files(redis, current_user.id, data.room_id)

    return MessageCreateResponse.model_validate(new_msg)


async def get_message_by_id(
    message_id: int, db: AsyncSession, current_user: User
) -> Optional[MessagePublic]:
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.files))
        .join(MessageStatus)
        .where(
            Message.id == message_id,
            MessageStatus.user_id == current_user.id,
            MessageStatus.status.in_(["delivered", "viewed"]),
        )
    )
    message = result.scalar_one_or_none()

    if not message:
        return None

    await db.execute(
        update(MessageStatus)
        .where(
            MessageStatus.message_id == message.id,
            MessageStatus.user_id == current_user.id,
        )
        .values(status="viewed", updated_at=datetime.datetime.now())
    )
    await db.commit()

    status_result = await db.execute(
        select(MessageStatus.status).where(
            MessageStatus.message_id == message.id,
            MessageStatus.user_id != current_user.id,
        )
    )
    status = status_result.scalar_one_or_none() or "sent"

    return MessagePublic(
        id=message.id,
        room_id=message.room_id,
        sender_id=message.sender.id,
        sender=MessageSender.model_validate(message.sender),
        content=message.content,
        created_at=message.created_at,
        updated_at=message.updated_at,
        files=[file.file_url for file in (message.files or []) if file is not None],
        status=status,
        is_owner=(message.sender_id == current_user.id),
    )


async def get_messages_by_room(
    room_id: int,
    db: AsyncSession,
    current_user: User,
    pagination: Pagination,
) -> List[MessagePublic]:
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.files), selectinload(Message.sender))
        .join(MessageStatus)
        .where(
            Message.room_id == room_id,
            MessageStatus.user_id == current_user.id,
            MessageStatus.status.in_(["delivered", "viewed"]),
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
            MessageStatus.user_id != current_user.id,
        )
        .values(status="viewed", updated_at=datetime.datetime.now())
    )
    await db.commit()

    status_result = await db.execute(
        select(MessageStatus.message_id, MessageStatus.status).where(
            MessageStatus.user_id == current_user.id,
            MessageStatus.message_id.in_([m.id for m in messages]),
        )
    )
    statuses = {mid: status for mid, status in status_result.scalars().all()}

    return [
        MessagePublic(
            id=msg.id,
            room_id=msg.room_id,
            sender_id=msg.sender.id,
            sender=MessageSender.model_validate(msg.sender),
            content=msg.content,
            created_at=msg.created_at,
            updated_at=msg.updated_at,
            files=[f.file_url for f in (msg.files or []) if f is not None],
            status=statuses.get(msg.id, "sent"),
            is_owner=(msg.sender_id == current_user.id),
        )
        for msg in messages
    ]


async def update_message(
    data: MessageUpdateRequest, db: AsyncSession, current_user: User
) -> MessageUpdateResponse:
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

    message.updated_at = datetime.datetime.now()

    await db.execute(delete(FileStorage).where(FileStorage.message_id == message.id))

    for url in data.file_urls:
        db.add(FileStorage(message_id=message.id, file_url=url))

    await db.execute(
        update(MessageStatus)
        .where(
            MessageStatus.message_id == message.id,
            MessageStatus.user_id != current_user.id,
            MessageStatus.status != "deleted",
        )
        .values(status="delivered", updated_at=datetime.datetime.now())
    )

    await db.commit()

    return MessageUpdateResponse(message_id=message.id)


async def delete_message(
    message_id: int, db: AsyncSession, current_user: User
) -> MessageDeleteResponse:
    await db.execute(
        update(MessageStatus)
        .where(
            MessageStatus.message_id == message_id,
            MessageStatus.user_id == current_user.id,
        )
        .values(status="deleted", updated_at=datetime.datetime.now())
    )
    await db.commit()
    return MessageDeleteResponse(message_id=message_id)


async def search_messages(
    room_id: int, text: Optional[str], db: AsyncSession, current_user: User
) -> list[MessagePublic]:
    query = (
        select(Message)
        .options(selectinload(Message.files), selectinload(Message.sender))
        .join(MessageStatus)
        .where(
            Message.room_id == room_id,
            MessageStatus.status.in_(["delivered", "viewed"]),
        )
        .order_by(Message.created_at)
    )

    if text:
        query = query.where(Message.content.ilike(f"%{text}%"))

    result = await db.execute(query)
    messages = result.scalars().all()

    return [
        MessagePublic(
            id=msg.id,
            room_id=msg.room_id,
            sender_id=msg.sender.id,
            sender=MessageSender.model_validate(msg.sender),
            content=msg.content,
            created_at=msg.created_at,
            updated_at=msg.updated_at,
            files=[f.file_url for f in (msg.files or []) if f is not None],
            status=None,
            is_owner=(msg.sender_id == current_user.id),
        )
        for msg in messages
    ]
