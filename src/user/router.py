from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_db, settings
from src.auth import get_current_user
from src.core import User
from src.user import service
from src.user.schemas import UsernameUpdateRequest, UsernameUpdateResponse, UserPublic

router = APIRouter(prefix="/user", tags=["user"])


@router.get(
    "/me", summary="Get current user", response_model=UserPublic, status_code=200
)
async def get_me(  # type: ignore[no-untyped-def]
    response: Response, result: tuple[User, str | None] = Depends(get_current_user)
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
    return await service.get_user_info(user)


@router.patch(
    "/username",
    summary="Update username",
    response_model=UsernameUpdateResponse,
    status_code=200,
)
async def patch_username(  # type: ignore[no-untyped-def]
    response: Response,
    data: UsernameUpdateRequest,
    db: AsyncSession = Depends(get_db),
    result: tuple[User, str | None] = Depends(get_current_user),
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
    return await service.update_username(data, db, user)


@router.get(
    "/search",
    summary="Search for users by username or email",
    response_model=list[UserPublic],
    status_code=200,
)
async def search_users(  # type: ignore[no-untyped-def]
    username: str | None = None,
    email: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await service.search_users(username, email, db)


@router.get(
    "/{user_id}", summary="Get user", response_model=UserPublic, status_code=200
)
async def get_user_by_id(  # type: ignore[no-untyped-def]
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_user_by_id(user_id, db)
