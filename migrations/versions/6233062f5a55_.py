"""empty message

Revision ID: 6233062f5a55
Revises: ff26486983c9
Create Date: 2020-03-21 10:25:04.805615

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6233062f5a55'
down_revision = 'ff26486983c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('language', sa.String(length=5), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'language')
    # ### end Alembic commands ###
