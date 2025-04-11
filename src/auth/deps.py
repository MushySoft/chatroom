from fastapi import Depends, Header, WebSocket, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from authlib.integrations.httpx_client import AsyncOAuth2Client
from src.deps import get_db
from src.core.models import User
from src.auth.exceptions import AuthException


async def get_current_user(
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthException("Неверный формат токена")

    token = authorization.split(" ")[1]

    async with AsyncOAuth2Client(token={"access_token": token, "token_type": "Bearer"}) as client:
        try:
            resp = await client.get("https://openidconnect.googleapis.com/v1/userinfo")
            resp.raise_for_status()
        except Exception:
            raise AuthException("Недействительный токен Google")

    user_info = resp.json()
    email = user_info.get("email")
    if not email:
        raise AuthException("Email не найден в профиле Google")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise AuthException("Пользователь не найден")

    return user


async def get_current_user_ws(
        websocket: WebSocket,
        db: AsyncSession = Depends(get_db)
) -> User:
    auth_header = websocket.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise AuthException("Неверный формат токена")

    token = auth_header.split(" ")[1]

    async with AsyncOAuth2Client(token={"access_token": token, "token_type": "Bearer"}) as client:
        try:
            resp = await client.get("https://openidconnect.googleapis.com/v1/userinfo")
            resp.raise_for_status()
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise AuthException("Недействительный токен Google")

    user_info = resp.json()
    email = user_info.get("email")
    if not email:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise AuthException("Email не найден в профиле Google")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise AuthException("Пользователь не найден")

    return user
