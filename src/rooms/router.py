from fastapi import APIRouter, Depends, HTTPException, Response
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.deps import get_current_user
from src import get_redis, get_db, Pagination, settings
from src.core.models import User
from src.rooms import service
from src.rooms.schemas import (
    RoomCreate, RoomInvite, RoomInviteRespond, RoomWithLastMessageOut, RoomUpdate
)

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/", summary="Create a rooms")
async def create_room(
        data: RoomCreate,
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
            max_age=settings.TOKEN_EXPIRE_SECONDS
        )
    return await service.create_room(
        data=data,
        db=db,
        current_user=user
    )


@router.post("/invite", summary="Invite user to a rooms")
async def invite_user(
        data: RoomInvite,
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
            max_age=settings.TOKEN_EXPIRE_SECONDS
        )
    try:
        return await service.invite_user(
            data=data,
            db=db,
            current_user=user
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/invitations/sent", summary="View sent invitations")
async def sent_invitations(
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        pagination: Pagination = Depends(Pagination),
        redis: Redis = Depends(get_redis)
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
            max_age=settings.TOKEN_EXPIRE_SECONDS
        )
    return await service.get_sent_invites(
        db=db,
        current_user=user,
        pagination=pagination,
        redis=redis
    )


@router.get("/invitations/received", summary="View received invitations")
async def received_invitations(
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        pagination: Pagination = Depends(Pagination),
        redis: Redis = Depends(get_redis)
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
            max_age=settings.TOKEN_EXPIRE_SECONDS
        )
    return await service.get_received_invites(
        db=db,
        current_user=user,
        pagination=pagination,
        redis=redis
    )


@router.post("/invitations/respond", summary="Respond to invitation")
async def respond_to_invite(
        data: RoomInviteRespond,
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis)
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
            max_age=settings.TOKEN_EXPIRE_SECONDS
        )
    try:
        return await service.respond_to_invite(
            data=data,
            db=db,
            current_user=user,
            redis=redis)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{room_id}/users/{user_id}", summary="Remove user from rooms")
async def remove_user(
        room_id: int,
        user_id: int,
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis)
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
            max_age=settings.TOKEN_EXPIRE_SECONDS
        )
    try:
        return await service.remove_user_from_room(
            room_id=room_id,
            user_id=user_id,
            db=db,
            current_user=user,
            redis=redis
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{room_id}/leave", summary="Leave rooms")
async def leave_room(
        room_id: int,
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis)
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
            max_age=settings.TOKEN_EXPIRE_SECONDS
        )
    return await service.leave_room(
        room_id=room_id,
        db=db,
        current_user=user,
        redis=redis
    )


@router.get("/{room_id}/participants", summary="List rooms participants")
async def get_participants(
        room_id: int,
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        pagination: Pagination = Depends(Pagination),
        redis: Redis = Depends(get_redis)
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
            max_age=settings.TOKEN_EXPIRE_SECONDS
        )
    return await service.get_room_participants(
        room_id=room_id,
        db=db,
        pagination=pagination,
        redis=redis
    )


@router.get("/all", response_model=list[RoomWithLastMessageOut])
async def get_all_rooms(
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        pagination: Pagination = Depends(Pagination),
        redis: Redis = Depends(get_redis)
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
            max_age=settings.TOKEN_EXPIRE_SECONDS
        )
    return await service.get_rooms(
        db=db,
        current_user=user,
        pagination=pagination,
        redis=redis,
    )


@router.patch("/{room_id}", summary="Update rooms settings")
async def patch_room(
        room_id: int,
        data: RoomUpdate,
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
            max_age=settings.TOKEN_EXPIRE_SECONDS
        )
    return await service.update_room(
        room_id=room_id,
        data=data,
        db=db,
        current_user=user
    )
