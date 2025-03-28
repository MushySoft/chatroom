from fastapi import APIRouter, Depends
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.dependencies import get_db
from src.auth import service

router = APIRouter()


@router.get("/auth/login")
async def login(request: Request):
    return await service.login(request)


@router.get("/auth/callback")
async def auth_callback(request: Request, db: AsyncSession = Depends(get_db)):
    return await service.auth_callback(request, db)
