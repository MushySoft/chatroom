from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.deps import get_db
from src.auth import service
from src.auth.schemas import UsernameUpdate
from src.auth.deps import get_current_user
from src.core.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login", summary="Login via Google")
async def login(request: Request):
    return await service.login(request)


@router.get("/callback", summary="Redirect to Google")
async def auth_callback(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    return await service.auth_callback(
        request=request,
        db=db
    )


@router.get("/me", summary="Get current user")
async def get_me(
    response: Response,
    result: tuple[User, str | None] = Depends(get_current_user)
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7
        )
    return await service.get_user_info(user)

@router.patch("/username", summary="Update username")
async def patch_username(
    data: UsernameUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.update_username(data, db, current_user)
