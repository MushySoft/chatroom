from fastapi import (
    Depends,
    Header,
    WebSocket,
    status,
    Cookie
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.httpx_client import AsyncOAuth2Client
from typing import Tuple, Optional

from src.deps import get_db
from src.core import User

from src.auth.exceptions import AuthException


async def get_current_user(
    authorization: str | None = Header(default=None, alias="Authorization"),
    token_cookie: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db)
) -> Tuple[User, Optional[str]]:
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    elif token_cookie:
        token = token_cookie
    else:
        raise AuthException("Токен не найден")

    async with AsyncOAuth2Client(token={"access_token": token, "token_type": "Bearer"}) as client:
        try:
            resp = await client.get("https://openidconnect.googleapis.com/v1/userinfo")
            resp.raise_for_status()
            user_info = resp.json()
            email = user_info.get("email")
        except Exception:
            try:
                token_info = await client.get("https://oauth2.googleapis.com/tokeninfo", params={"access_token": token})
                token_info.raise_for_status()
                auth_id = token_info.json().get("sub")
            except Exception:
                raise AuthException("access_token и auth_id недействительны")

            result = await db.execute(select(User).where(User.auth_id == auth_id))
            user = result.scalar_one_or_none()
            if not user or not user.refresh_token:
                raise AuthException("Пользователь не найден или нет refresh_token")
            try:
                new_token = await client.refresh_token(
                    url="https://oauth2.googleapis.com/token",
                    refresh_token=user.refresh_token
                )
                new_access_token = new_token["access_token"]
                client.token = {"access_token": new_access_token, "token_type": "Bearer"}

                resp = await client.get("https://openidconnect.googleapis.com/v1/userinfo")
                resp.raise_for_status()
                user_info = resp.json()
                email = user_info.get("email")
            except Exception:
                raise AuthException("Не удалось обновить токен")

            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if not user:
                raise AuthException("Пользователь не найден")

            return user, new_access_token

    if not email:
        raise AuthException("Email не найден в профиле Google")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise AuthException("Пользователь не найден")

    return user, None


async def get_current_user_ws(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
    token_cookie: str | None = Cookie(default=None)
) -> User:
    auth_header = websocket.headers.get("authorization")

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif token_cookie:
        token = token_cookie
    else:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise AuthException("Токен не найден")

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
