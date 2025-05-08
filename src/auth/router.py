from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import service
from src.auth.deps import get_current_user
from src.core import User
from src.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login", summary="Login via Google", status_code=200)
async def login(request: Request):  # type: ignore[no-untyped-def]
    return await service.login(request)


@router.get("/callback", summary="Redirect to Google", status_code=302)
async def auth_callback(  # type: ignore[no-untyped-def]
    request: Request, db: AsyncSession = Depends(get_db)
):
    return await service.auth_callback(request=request, db=db)


@router.get("/logout", summary="Logout", status_code=204)
async def logout(  # type: ignore[no-untyped-def]
    db: AsyncSession = Depends(get_db),
    result: tuple[User, str | None] = Depends(get_current_user),
):
    user, new_token = result
    return await service.logout(db, user)
