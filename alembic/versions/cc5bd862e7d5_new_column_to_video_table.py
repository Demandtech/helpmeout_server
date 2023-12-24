"""new column to video table

Revision ID: cc5bd862e7d5
Revises: 86d5583fba07
Create Date: 2023-11-19 19:01:44.592434

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc5bd862e7d5'
down_revision: Union[str, None] = '86d5583fba07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('videos', sa.Column('duration', sa.Float(), server_default=sa.text('0.0'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('videos', 'duration')
    # ### end Alembic commands ###