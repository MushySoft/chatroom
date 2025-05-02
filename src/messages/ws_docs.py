from fastapi import APIRouter

router = APIRouter(tags=["WebSocket Docs"], prefix="/docs/ws/chat")


@router.get("", summary="WebSocket Chat API", description="Description WebSocket API for chat")
def ws_chat_docs():
    return {
        "endpoint": "ws://your-domain/ws/chat/{room_id}",
        "description": "WebSocket connection to chat rooms",
        "actions": {
            "send_message": {
                "data": {
                    "room_id": "int",
                    "text": "str"
                },
                "response": {
                    "type": "new_message",
                    "data": "Message schema"
                }
            },
            "get_messages": {
                "response": {
                    "type": "message_history",
                    "data": "[Message schema]"
                }
            },
            "get_message": {
                "message_id": "int",
                "response": {
                    "type": "message_detail",
                    "data": "Message schema"
                }
            },
            "edit_message": {
                "data": {
                    "message_id": "int",
                    "text": "str"
                },
                "response": {
                    "type": "message_edited",
                    "data": "Message schema"
                }
            },
            "delete_message": {
                "message_id": "int",
                "response": {
                    "type": "message_deleted",
                    "data": {
                        "message_id": "int"
                    }
                }
            }
        }
    }
