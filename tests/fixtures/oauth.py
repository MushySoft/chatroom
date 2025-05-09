from unittest.mock import AsyncMock

import pytest_asyncio


@pytest_asyncio.fixture(autouse=True)
def patch_google_oauth(monkeypatch):
    monkeypatch.setattr(
        "src.auth.service.oauth.google.authorize_redirect",
        AsyncMock(return_value={"redirect": "https://google.com/redirect"}),
    )
    monkeypatch.setattr(
        "src.auth.service.oauth.google.authorize_access_token",
        AsyncMock(
            return_value={
                "access_token": "mock_token",
                "refresh_token": "mock_refresh_token",
            }
        ),
    )
    monkeypatch.setattr(
        "src.auth.service.oauth.google.userinfo",
        AsyncMock(
            return_value={
                "email": "test@example.com",
                "name": "TestUser",
                "sub": "1234567890",
                "picture": None,
            }
        ),
    )
