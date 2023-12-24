"""remove column from video table

Revision ID: f1a819f00bba
Revises: cc5bd862e7d5
Create Date: 2023-11-20 06:21:23.641044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a819f00bba'
down_revision: Union[str, None] = 'cc5bd862e7d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('videos', 'video_duration')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('videos', sa.Column('video_duration', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
