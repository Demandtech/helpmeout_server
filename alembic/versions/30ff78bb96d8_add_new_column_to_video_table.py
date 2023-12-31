"""add new column to video table

Revision ID: 30ff78bb96d8
Revises: f1a819f00bba
Create Date: 2023-11-20 08:41:51.085954

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30ff78bb96d8'
down_revision: Union[str, None] = 'f1a819f00bba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('videos', sa.Column('video_path', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('videos', 'video_path')
    # ### end Alembic commands ###
