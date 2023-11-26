"""adding peer_id and is_online check

Revision ID: d52d9ddc01d3
Revises: 3ce16cf5b573
Create Date: 2023-11-25 19:04:48.214981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd52d9ddc01d3'
down_revision = '3ce16cf5b573'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('peer_id', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('is_online', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_online')
        batch_op.drop_column('peer_id')

    # ### end Alembic commands ###