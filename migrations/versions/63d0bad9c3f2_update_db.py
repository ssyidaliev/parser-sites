"""update db

Revision ID: 63d0bad9c3f2
Revises: 540af16bfb95
Create Date: 2021-11-21 18:12:33.730542

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63d0bad9c3f2'
down_revision = '540af16bfb95'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'logging_record', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'logging_record', type_='unique')
    # ### end Alembic commands ###