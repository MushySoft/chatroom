from fastapi import APIRouter, Depends, HTTPException, Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src import Pagination, get_db, get_redis, settings
from src.auth import get_current_user
from src.core import User
from src.rooms import service
from src.rooms.schemas import (
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

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post(
    "/", summary="Create a rooms", response_model=RoomCreateResponse, status_code=201
)
async def create_room(  # type: ignore[no-untyped-def]
    data: RoomCreateRequest,
    response: Response,
    result: tuple[User, str | None] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.create_room(data=data, db=db, current_user=user)


@router.post(
    "/invite",
    summary="Invite user to a rooms",
    response_model=RoomInviteResponse,
    status_code=201,
)
async def invite_user(  # type: ignore[no-untyped-def]
    data: RoomInviteRequest,
    response: Response,
    result: tuple[User, str | None] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    try:
        return await service.invite_user(data=data, db=db, current_user=user)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get(
    "/invitations/sent",
    summary="View sent invitations",
    response_model=list[RoomInvitationOut],
    status_code=200,
)
async def get_sent_invitations(  # type: ignore[no-untyped-def]
    response: Response,
    result: tuple[User, str | None] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(Pagination),
    redis: Redis = Depends(get_redis),
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.get_sent_invites(
        db=db, current_user=user, pagination=pagination, redis=redis
    )


@router.get(
    "/invitations/received",
    summary="View received invitations",
    response_model=list[RoomInvitationOut],
    status_code=200,
)
async def received_invitations(  # type: ignore[no-untyped-def]
    response: Response,
    result: tuple[User, str | None] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(Pagination),
    redis: Redis = Depends(get_redis),
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.get_received_invites(
        db=db, current_user=user, pagination=pagination, redis=redis
    )


@router.post(
    "/invitations/respond",
    summary="Respond to invitation",
    response_model=RoomInviteRespondResponse,
    status_code=200,
)
async def respond_to_invite(  # type: ignore[no-untyped-def]
    data: RoomInviteRespondRequest,
    response: Response,
    result: tuple[User, str | None] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    try:
        return await service.respond_to_invite(
            data=data, db=db, current_user=user, redis=redis
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete(
    "/{room_id}/users/{user_id}",
    summary="Remove user from rooms",
    response_model=RemoveUserResponse,
    status_code=200,
)
async def remove_user(  # type: ignore[no-untyped-def]
    room_id: int,
    user_id: int,
    response: Response,
    result: tuple[User, str | None] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )

        return await service.remove_user_from_room(
            room_id=room_id, user_id=user_id, db=db, current_user=user, redis=redis
        )


@router.delete(
    "/{room_id}/leave",
    summary="Leave rooms",
    response_model=LeaveRoomResponse,
    status_code=200,
)
async def leave_room(  # type: ignore[no-untyped-def]
    room_id: int,
    response: Response,
    result: tuple[User, str | None] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.leave_room(
        room_id=room_id, db=db, current_user=user, redis=redis
    )


@router.get(
    "/{room_id}/participants",
    summary="List rooms participants",
    response_model=list[RoomParticipantOut],
    status_code=200,
)
async def get_participants(  # type: ignore[no-untyped-def]
    room_id: int,
    response: Response,
    result: tuple[User, str | None] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(Pagination),
    redis: Redis = Depends(get_redis),
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.get_room_participants(
        room_id=room_id, db=db, pagination=pagination, redis=redis
    )


@router.get("/all", response_model=list[RoomWithLastMessageOut], status_code=200)
async def get_all_rooms(  # type: ignore[no-untyped-def]
    response: Response,
    result: tuple[User, str | None] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(Pagination),
    redis: Redis = Depends(get_redis),
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.get_rooms(
        db=db,
        current_user=user,
        pagination=pagination,
        redis=redis,
    )


@router.patch(
    "/{room_id}",
    summary="Update rooms settings",
    response_model=RoomUpdateResponse,
    status_code=200,
)
async def patch_room(  # type: ignore[no-untyped-def]
    room_id: int,
    data: RoomUpdateRequest,
    response: Response,
    result: tuple[User, str | None] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.update_room(
        room_id=room_id, data=data, db=db, current_user=user
    )
