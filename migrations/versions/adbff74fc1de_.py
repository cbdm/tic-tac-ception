"""empty message

Revision ID: adbff74fc1de
Revises: 
Create Date: 2021-01-30 10:30:33.372825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adbff74fc1de'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('saved_games',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.String(), nullable=True),
    sa.Column('xPASS', sa.String(), nullable=True),
    sa.Column('oPASS', sa.String(), nullable=True),
    sa.Column('board', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('saved_games')
    # ### end Alembic commands ###
