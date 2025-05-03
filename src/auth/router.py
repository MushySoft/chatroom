from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.deps import get_db
from src.core import User

from src.auth import service
from src.auth.deps import get_current_user

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


@router.get("/logout", summary="Logout")
async def logout(
        db: AsyncSession = Depends(get_db),
        result: tuple[User, str | None] = Depends(get_current_user)
):
    user, new_token = result
    return await service.logout(db, user)
