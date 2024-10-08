"""add username

Revision ID: a9526dcf08bf
Revises: e6b4b582f39f
Create Date: 2024-10-01 00:24:35.944059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9526dcf08bf'
down_revision: Union[str, None] = 'e6b4b582f39f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('username', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'username')
    # ### end Alembic commands ###
