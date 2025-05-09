from datetime import datetime
from unittest.mock import MagicMock


class MockUser:
    id = 1
    username = "TestUser"
    email = "test@example.com"
    refresh_token = "mock_refresh_token"
    status = MagicMock(status="active")
    avatar_url = "mock_url"


class MockUser2:
    id = 2
    username = "SecondUser"
    email = "second@example.com"
    refresh_token = "second_refresh_token"
    status = MagicMock(status="active")
    avatar_url = "mock_url"


class MockRoom:
    def __init__(self):
        self.id = 1
        self.name = "Test Room"
        self.is_private = False
        self.created_by = 1
        self.created_at = self.updated_at = datetime(2024, 1, 1)


class MockRoomInvitation:
    def __init__(self):
        self.id = 1
        self.room_id = 1
        self.sender_id = 1
        self.receiver_id = 2
        self.created_at = datetime(2024, 1, 1)
        self.status = MagicMock(status="pending")


class MockRoomUser:
    def __init__(self):
        self.id = 1
        self.room_id = 1
        self.user_id = 1
        self.joined_at = datetime(2024, 1, 1)


class MockMessage:
    def __init__(self):
        self.id = 1
        self.room_id = 1
        self.sender_id = 1
        self.sender = MockUser()
        self.content = "Hello!"
        self.created_at = self.updated_at = datetime(2024, 1, 1)
        self.files = [MockFileStorage("https://example.com/file.jpg")]
        self.status = MockMessageStatus(self.id, self.sender_id, "delivered")
        self.is_owner = True


class MockFileStorage:
    def __init__(self, url):
        self.file_url = url


class MockMessageStatus:
    def __init__(self, message_id, user_id, status):
        self.message_id = message_id
        self.user_id = user_id
        self.status = status
        self.updated_at = datetime(2024, 1, 1)
