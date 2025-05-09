import json
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from src.auth.deps import get_current_user, get_current_user_ws
from src.deps import get_db as real_get_db
from src.deps import get_redis as real_get_redis
from src.main import app
from tests.mocks import (
    MockMessage,
    MockRoom,
    MockRoomInvitation,
    MockRoomUser,
    MockUser,
    MockUser2,
)


# noinspection PyUnreachableCode
def get_client(active_user: int = 1, for_ws: bool = False):
    mock_db = AsyncMock()
    mock_redis = AsyncMock()

    mock_user1 = MockUser()
    mock_user2 = MockUser2()
    mock_room = MockRoom()
    mock_invitation = MockRoomInvitation()
    mock_room_user = MockRoomUser()
    mock_message = MockMessage()

    current_user = mock_user1 if active_user == 1 else mock_user2

    # noinspection PyTypeChecker
    async def flush_side_effect():
        for call in mock_db.add.call_args_list:
            obj = call.args[0]
            if getattr(obj, "id", None) is None:
                obj.id = 1

    mock_db.flush.side_effect = flush_side_effect
    mock_db.commit = AsyncMock()
    mock_db.add = MagicMock()

    async def db_execute_mock(query):
        class Result:
            def scalar_one_or_none(self):
                q = str(query).lower()
                if "users" in q:
                    return mock_user2 if "2" in q else mock_user1
                if "messages" in q:
                    return mock_message
                if "rooms" in q:
                    return mock_room
                if "room_invitations" in q:
                    return mock_invitation
                if "room_user" in q:
                    return mock_room_user
                return None

            def scalars(self):
                class Scalars:
                    def all(inner_self):
                        if "from users" in str(query).lower():
                            return [mock_user1, mock_user2]
                        elif "from rooms" in str(query).lower():
                            return [mock_room]
                        elif "from messages" in str(query).lower():
                            return [mock_message]
                        return []

                return Scalars()

        return Result()

    mock_db.execute.side_effect = db_execute_mock

    mock_redis.get.return_value = json.dumps([])

    mock_oauth = AsyncMock()
    mock_oauth.__aenter__.return_value.get.return_value.status_code = 200
    mock_oauth.__aenter__.return_value.get.return_value.json.return_value = {
        "email": mock_user1.email if active_user == 1 else mock_user2.email,
    }

    with (
        patch("src.auth.deps.AsyncOAuth2Client", return_value=mock_oauth),
        patch("src.cache.get_cached_invites", return_value=[]),
        patch("src.cache.get_cached_participants", return_value=[]),
        patch("src.cache.get_cached_rooms", return_value=[]),
    ):

        app.dependency_overrides[real_get_db] = lambda: mock_db
        app.dependency_overrides[real_get_redis] = lambda: mock_redis
        app.dependency_overrides[get_current_user] = lambda: (current_user, None)
        if for_ws:
            app.dependency_overrides[get_current_user_ws] = lambda: current_user
        return TestClient(app)
        app.dependency_overrides = {}
