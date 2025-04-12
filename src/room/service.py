from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi import HTTPException

from src.core.models import (
    Room, RoomUser, RoomInvitation, RoomInvitationStatus,
    User, Message
)
from src.room.schemas import (
    RoomCreate, RoomInvite, RoomInviteRespond, RoomUpdate
)


async def create_room(data: RoomCreate, db: AsyncSession, current_user: User):
    new_room = Room(
        name=data.name,
        is_private=data.is_private,
        created_by=current_user.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(new_room)
    await db.flush()

    db.add(RoomUser(room_id=new_room.id, user_id=current_user.id, joined_at=datetime.now()))
    await db.commit()
    return new_room


async def invite_user(data: RoomInvite, db: AsyncSession, current_user: User):
    result = await db.execute(
        select(RoomUser).where(
            RoomUser.room_id == data.room_id,
            RoomUser.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise PermissionError("You are not a member of this room")

    invitation = RoomInvitation(
        room_id=data.room_id,
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        created_at=datetime.now()
    )
    db.add(invitation)
    await db.flush()

    db.add(RoomInvitationStatus(
        invitation_id=invitation.id,
        status="pending",
        updated_at=datetime.now()
    ))
    await db.commit()
    return {"invitation_id": invitation.id, "status": "pending"}


async def get_sent_invites(db: AsyncSession, current_user: User):
    result = await db.execute(
        select(RoomInvitation)
        .join(RoomInvitationStatus)
        .where(RoomInvitation.sender_id == current_user.id)
    )
    return result.scalars().all()


async def get_received_invites(db: AsyncSession, current_user: User):
    result = await db.execute(
        select(RoomInvitation)
        .join(RoomInvitationStatus)
        .where(RoomInvitation.receiver_id == current_user.id)
    )
    return result.scalars().all()


async def respond_to_invite(data: RoomInviteRespond, db: AsyncSession, current_user: User):
    result = await db.execute(
        select(RoomInvitation)
        .where(RoomInvitation.id == data.invitation_id)
    )
    invitation = result.scalar_one_or_none()

    if not invitation or invitation.receiver_id != current_user.id:
        raise PermissionError("You are not allowed to respond to this invite")

    status = "accepted" if data.accept else "rejected"
    await db.execute(
        update(RoomInvitationStatus)
        .where(RoomInvitationStatus.invitation_id == invitation.id)
        .values(status=status, updated_at=datetime.now())
    )

    if data.accept:
        db.add(RoomUser(
            room_id=invitation.room_id,
            user_id=current_user.id,
            joined_at=datetime.now()
        ))

    await db.commit()
    return {"status": status}


async def remove_user_from_room(room_id: int, user_id: int, db: AsyncSession, current_user: User):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room or room.created_by != current_user.id:
        raise PermissionError("Only the room owner can remove users")

    await db.execute(
        delete(RoomUser)
        .where(RoomUser.room_id == room_id, RoomUser.user_id == user_id)
    )
    await db.commit()
    return {"status": "removed"}


async def leave_room(room_id: int, db: AsyncSession, current_user: User):
    await db.execute(
        delete(RoomUser)
        .where(RoomUser.room_id == room_id, RoomUser.user_id == current_user.id)
    )
    await db.commit()
    return {"status": "left"}


async def get_room_participants(room_id: int, db: AsyncSession):
    result = await db.execute(
        select(RoomUser).where(RoomUser.room_id == room_id)
    )
    return result.scalars().all()


async def get_rooms(
    db: AsyncSession,
    current_user: User
):
    # 1. Получить комнаты пользователя
    result = await db.execute(
        select(Room)
        .join(RoomUser)
        .where(RoomUser.user_id == current_user.id)
    )
    rooms = result.scalars().all()

    room_data = []
    for room in rooms:
        # 2. Последнее сообщение в комнате
        msg_result = await db.execute(
            select(Message)
            .where(Message.room_id == room.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_msg = msg_result.scalar_one_or_none()

        room_data.append({
            "id": room.id,
            "name": room.name,
            "is_private": room.is_private,
            "created_by": room.created_by,
            "created_at": room.created_at,
            "last_message": {
                "id": last_msg.id,
                "content": last_msg.content,
                "created_at": last_msg.created_at,
                "sender_id": last_msg.sender_id
            } if last_msg else None
        })

    return room_data


async def update_room(
    room_id: int,
    data: RoomUpdate,
    db: AsyncSession,
    current_user: User
):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of this room")

    if data.name is not None:
        room.name = data.name

    if data.is_private is not None:
        room.is_private = data.is_private

    room.updated_at = datetime.now()
    await db.commit()
    return {"status": "updated"}
