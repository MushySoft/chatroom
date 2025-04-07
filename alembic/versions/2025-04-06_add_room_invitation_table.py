"""add room invitation table

Revision ID: 75839776779a
Revises: be7472cdfb11
Create Date: 2025-04-06 20:27:30.158026

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75839776779a'
down_revision: Union[str, None] = 'be7472cdfb11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('room_invitations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('room_id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('receiver_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_room_invitations_id'), 'room_invitations', ['id'], unique=False)
    op.create_table('room_invitation_statuses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('invitation_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'accepted', 'rejected', name='invitation_status_enum'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.ForeignKeyConstraint(['invitation_id'], ['room_invitations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_room_invitation_statuses_id'), 'room_invitation_statuses', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_room_invitation_statuses_id'), table_name='room_invitation_statuses')
    op.drop_table('room_invitation_statuses')
    op.drop_index(op.f('ix_room_invitations_id'), table_name='room_invitations')
    op.drop_table('room_invitations')
    # ### end Alembic commands ###
