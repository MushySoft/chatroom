from fastapi import APIRouter, Depends
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.deps import get_db
from src.auth import service
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
async def get_me(user: User = Depends(get_current_user)):
    return {
        "username": user.username,
        "email": user.email,
        "id": user.id
    }
