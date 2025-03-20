"""new table

Revision ID: cfae7a1a0013
Revises: 9821378377fb
Create Date: 2025-03-20 10:05:52.936329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cfae7a1a0013'
down_revision: Union[str, None] = '9821378377fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('notifications_user_id_fkey', 'notifications', type_='foreignkey')
    op.drop_column('notifications', 'user_id')
    op.drop_column('notifications', 'date')
    op.drop_column('users', 'is_admin')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_admin', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('notifications', sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('notifications', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('notifications_user_id_fkey', 'notifications', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###
