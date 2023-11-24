"""Initial migration.

Revision ID: f8a43ae859a2
Revises: 
Create Date: 2023-11-24 12:49:45.937756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8a43ae859a2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('phone_number', sa.Integer(), nullable=True),
    sa.Column('profile_pic', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('call_logs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('sender_user_id', sa.Integer(), nullable=False),
    sa.Column('receiver_user_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('duration', sa.Time(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['receiver_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['sender_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('call_logs')
    op.drop_table('users')
    # ### end Alembic commands ###
