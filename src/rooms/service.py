import datetime
import json

from fastapi import HTTPException
from redis.asyncio import Redis
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src import Pagination
from src.cache import (
    delete_cached_participants,
    get_cached_invites,
    get_cached_participants,
    get_cached_rooms,
    set_cached_invites,
    set_cached_participants,
    set_cached_rooms,
)
from src.core import Message, Room, RoomInvitation, RoomInvitationStatus, RoomUser, User
from src.rooms.schemas import (
    LastMessageOut,
    LeaveRoomResponse,
    RemoveUserResponse,
    RoomCreateRequest,
    RoomCreateResponse,
    RoomInvitationOut,
    RoomInviteRequest,
    RoomInviteRespondRequest,
    RoomInviteRespondResponse,
    RoomInviteResponse,
    RoomParticipantOut,
    RoomUpdateRequest,
    RoomUpdateResponse,
    RoomWithLastMessageOut,
)


async def create_room(
    data: RoomCreateRequest, db: AsyncSession, current_user: User
) -> RoomCreateResponse:
    new_room = Room(
        name=data.name,
        is_private=data.is_private,
        created_by=current_user.id,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    db.add(new_room)
    await db.flush()

    db.add(
        RoomUser(
            room_id=new_room.id,
            user_id=current_user.id,
            joined_at=datetime.datetime.now(),
        )
    )
    await db.commit()
    return RoomCreateResponse(
        id=new_room.id,
        name=new_room.name,
        is_private=new_room.is_private,
        created_by=new_room.created_by,
        created_at=new_room.created_at,
        updated_at=new_room.updated_at,
    )


async def invite_user(
    data: RoomInviteRequest, db: AsyncSession, current_user: User
) -> RoomInviteResponse:
    result = await db.execute(
        select(RoomUser).where(
            RoomUser.room_id == data.room_id, RoomUser.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise PermissionError("You are not a member of this rooms")

    invitation = RoomInvitation(
        room_id=data.room_id,
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        created_at=datetime.datetime.now(),
    )
    db.add(invitation)
    await db.flush()

    db.add(
        RoomInvitationStatus(
            invitation_id=invitation.id,
            status="pending",
            updated_at=datetime.datetime.now(),
        )
    )
    await db.commit()
    return RoomInviteResponse(invitation_id=invitation.id)


async def get_sent_invites(
    db: AsyncSession, current_user: User, pagination: Pagination, redis: Redis
) -> list[RoomInvitationOut] | None:
    cached = await get_cached_invites(
        redis,
        current_user.id,
        sent=True,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    if cached:
        return [RoomInvitationOut.model_validate(json.loads(c)) for c in cached]

    result = await db.execute(
        select(RoomInvitation)
        .join(RoomInvitationStatus)
        .where(RoomInvitation.sender_id == current_user.id)
        .limit(pagination.limit)
        .offset(pagination.offset)
    )
    invites = result.scalars().all()

    data = [
        RoomInvitationOut(
            id=i.id,
            room_id=i.room_id,
            sender_id=i.sender_id,
            receiver_id=i.receiver_id,
            status=i.status.status,
            created_at=i.created_at,
        )
        for i in invites
    ]
    await set_cached_invites(
        redis=redis,
        user_id=current_user.id,
        sent=True,
        limit=pagination.limit,
        offset=pagination.offset,
        data=[i.model_dump_json() for i in data],
    )
    return data


async def get_received_invites(
    db: AsyncSession, current_user: User, pagination: Pagination, redis: Redis
) -> list[RoomInvitationOut] | None:
    cached = await get_cached_invites(
        redis=redis,
        user_id=current_user.id,
        sent=False,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    if cached:
        return [RoomInvitationOut.model_validate(json.loads(c)) for c in cached]

    result = await db.execute(
        select(RoomInvitation)
        .join(RoomInvitationStatus)
        .where(RoomInvitation.receiver_id == current_user.id)
        .limit(pagination.limit)
        .offset(pagination.offset)
    )
    invites = result.scalars().all()

    data = [
        RoomInvitationOut(
            id=i.id,
            room_id=i.room_id,
            sender_id=i.sender_id,
            receiver_id=i.receiver_id,
            status=i.status.status,
            created_at=i.created_at,
        )
        for i in invites
    ]
    await set_cached_invites(
        redis=redis,
        user_id=current_user.id,
        sent=False,
        limit=pagination.limit,
        offset=pagination.offset,
        data=[i.model_dump_json() for i in data],
    )
    return data


async def respond_to_invite(
    data: RoomInviteRespondRequest, db: AsyncSession, current_user: User, redis: Redis
) -> RoomInviteRespondResponse:
    result = await db.execute(
        select(RoomInvitation).where(RoomInvitation.id == data.invitation_id)
    )
    invitation = result.scalar_one_or_none()

    if not invitation or invitation.receiver_id != current_user.id:
        raise PermissionError("You are not allowed to respond to this invite")

    status = "accepted" if data.accept else "rejected"
    await db.execute(
        update(RoomInvitationStatus)
        .where(RoomInvitationStatus.invitation_id == invitation.id)
        .values(status=status, updated_at=datetime.datetime.now())
    )

    if data.accept:
        db.add(
            RoomUser(
                room_id=invitation.room_id,
                user_id=current_user.id,
                joined_at=datetime.datetime.now(),
            )
        )
        await delete_cached_participants(redis=redis, room_id=invitation.room_id)

    await db.commit()
    return RoomInviteRespondResponse(status=status)


async def remove_user_from_room(
    room_id: int, user_id: int, db: AsyncSession, current_user: User, redis: Redis
) -> RemoveUserResponse:
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room or room.created_by != current_user.id:
        raise PermissionError("Only the rooms owner can remove users")

    await db.execute(
        delete(RoomUser).where(RoomUser.room_id == room_id, RoomUser.user_id == user_id)
    )
    await db.commit()
    await delete_cached_participants(redis=redis, room_id=room_id)
    return RemoveUserResponse()


async def leave_room(
    room_id: int, db: AsyncSession, current_user: User, redis: Redis
) -> LeaveRoomResponse:
    await db.execute(
        delete(RoomUser).where(
            RoomUser.room_id == room_id, RoomUser.user_id == current_user.id
        )
    )
    await db.commit()
    await delete_cached_participants(redis=redis, room_id=room_id)
    return LeaveRoomResponse()


async def get_room_participants(
    room_id: int, db: AsyncSession, pagination: Pagination, redis: Redis
) -> list[RoomParticipantOut] | None:
    cached = await get_cached_participants(redis, room_id)
    if cached:
        return [RoomParticipantOut.model_validate(json.loads(c)) for c in cached]

    result = await db.execute(
        select(RoomUser)
        .where(RoomUser.room_id == room_id)
        .limit(pagination.limit)
        .offset(pagination.offset)
    )
    participants = result.scalars().all()

    data = [RoomParticipantOut.model_validate(p) for p in participants]

    await set_cached_participants(
        redis=redis, room_id=room_id, data=[i.model_dump_json() for i in data]
    )
    return data


async def get_rooms(
    db: AsyncSession,
    redis: Redis,
    current_user: User,
    pagination: Pagination,
) -> list[RoomWithLastMessageOut] | None:
    cached = await get_cached_rooms(
        redis, current_user.id, pagination.limit, pagination.offset
    )
    if cached:
        return [RoomWithLastMessageOut.model_validate(json.loads(c)) for c in cached]

    result = await db.execute(
        select(Room)
        .join(RoomUser)
        .where(RoomUser.user_id == current_user.id)
        .limit(pagination.limit)
        .offset(pagination.offset)
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
            RoomWithLastMessageOut(
                id=room.id,
                name=room.name,
                is_private=room.is_private,
                created_by=room.created_by,
                created_at=room.created_at,
                last_message=(
                    LastMessageOut(
                        id=last_msg.id,
                        content=last_msg.content,
                        created_at=last_msg.created_at,
                        sender_id=last_msg.sender_id,
                    )
                    if last_msg
                    else None
                ),
            )
        )

    await set_cached_rooms(
        redis=redis,
        user_id=current_user.id,
        limit=pagination.limit,
        offset=pagination.offset,
        data=[r.model_dump_json() for r in room_data],
    )
    return room_data


async def update_room(
    room_id: int, data: RoomUpdateRequest, db: AsyncSession, current_user: User
) -> RoomUpdateResponse:
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.created_by != current_user.id:
        raise HTTPException(
            status_code=403, detail="You are not the owner of this rooms"
        )

    if data.name is not None:
        room.name = data.name

    if data.is_private is not None:
        room.is_private = data.is_private

    room.updated_at = datetime.datetime.now()
    await db.commit()
    return RoomUpdateResponse()


async def get_room_user_ids(room_id: int, db: AsyncSession) -> list[int]:
    result = await db.execute(
        select(RoomUser.user_id).where(RoomUser.room_id == room_id)
    )
    return list(result.scalars().all())
