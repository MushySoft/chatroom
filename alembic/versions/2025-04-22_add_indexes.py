"""add indexes

Revision ID: d66304d3bd3a
Revises: b6fc15413ccc
Create Date: 2025-04-22 10:46:07.136037

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d66304d3bd3a"
down_revision: Union[str, None] = "b6fc15413ccc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        "ix_message_status_message_id", "message_status", ["message_id"], unique=False
    )
    op.create_index(
        "ix_message_status_user_id", "message_status", ["user_id"], unique=False
    )
    op.create_index("ix_messages_created_at", "messages", ["created_at"], unique=False)
    op.create_index("ix_messages_room_id", "messages", ["room_id"], unique=False)
    op.create_index("ix_messages_sender_id", "messages", ["sender_id"], unique=False)
    op.create_index(
        "ix_room_invitations_receiver_id",
        "room_invitations",
        ["receiver_id"],
        unique=False,
    )
    op.create_index(
        "ix_room_invitations_sender_id", "room_invitations", ["sender_id"], unique=False
    )
    op.create_index("ix_room_user_room_id", "room_user", ["room_id"], unique=False)
    op.create_index("ix_room_user_user_id", "room_user", ["user_id"], unique=False)
    op.create_index("ix_user_status_user_id", "user_status", ["user_id"], unique=False)
    op.create_index("ix_users_auth_id", "users", ["auth_id"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_auth_id", table_name="users")
    op.drop_index("ix_user_status_user_id", table_name="user_status")
    op.drop_index("ix_room_user_user_id", table_name="room_user")
    op.drop_index("ix_room_user_room_id", table_name="room_user")
    op.drop_index("ix_room_invitations_sender_id", table_name="room_invitations")
    op.drop_index("ix_room_invitations_receiver_id", table_name="room_invitations")
    op.drop_index("ix_messages_sender_id", table_name="messages")
    op.drop_index("ix_messages_room_id", table_name="messages")
    op.drop_index("ix_messages_created_at", table_name="messages")
    op.drop_index("ix_message_status_user_id", table_name="message_status")
    op.drop_index("ix_message_status_message_id", table_name="message_status")
    # ### end Alembic commands ###
