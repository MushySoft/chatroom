from fastapi import APIRouter

router = APIRouter(prefix="/docs/ws", tags=["WebSocket Docs"])


@router.get("", summary="Global WebSocket API", description="Global Websocket `/ws`")
def websocket_global_docs():
    return {
        "endpoint": "ws://your-domain/ws",
        "description": "Global WebSocket (online, preview, invites, etc.)",
        "actions": {
            "get_room_list": {
                "description": "Receive room list with last messages",
                "request": {"action": "get_room_list"},
                "response": {
                    "type": "room_list",
                    "data": [
                        {
                            "id": "int",
                            "name": "str",
                            "last_message": {
                                "id": "int",
                                "content": "str",
                                "created_at": "ISO datetime",
                                "sender_id": "int",
                            },
                        }
                    ],
                },
            }
        },
        "push_types": {
            "last_message_update": {
                "description": "Push-notification about last message update",
                "data": {
                    "room_id": "int",
                    "last_message": {
                        "id": "int",
                        "content": "str",
                        "created_at": "ISO datetime",
                        "sender_id": "int",
                    },
                },
            },
            "user_online": {
                "description": "Push, that online",
                "data": {"user_id": "int"},
            },
            "user_offline": {
                "description": "Push, that ofline",
                "data": {"user_id": "int"},
            },
        },
    }
