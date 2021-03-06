"""empty message

Revision ID: 44ac09b089b6
Revises: 6233062f5a55
Create Date: 2020-03-23 11:47:56.321932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44ac09b089b6'
down_revision = '6233062f5a55'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lable_evalution',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('leval', sa.Integer(), nullable=True),
    sa.Column('cost_perform', sa.Integer(), nullable=True),
    sa.Column('appearance', sa.Integer(), nullable=True),
    sa.Column('applicability', sa.Integer(), nullable=True),
    sa.Column('laber', sa.String(length=16), nullable=True),
    sa.Column('is_labled', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lable_evalution_is_labled'), 'lable_evalution', ['is_labled'], unique=False)
    op.create_index(op.f('ix_lable_evalution_laber'), 'lable_evalution', ['laber'], unique=False)
    op.create_index(op.f('ix_lable_evalution_source_id'), 'lable_evalution', ['source_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_lable_evalution_source_id'), table_name='lable_evalution')
    op.drop_index(op.f('ix_lable_evalution_laber'), table_name='lable_evalution')
    op.drop_index(op.f('ix_lable_evalution_is_labled'), table_name='lable_evalution')
    op.drop_table('lable_evalution')
    # ### end Alembic commands ###
