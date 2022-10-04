"""empty message

Revision ID: 84b8ea271204
Revises: 
Create Date: 2022-10-04 10:05:38.303080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84b8ea271204'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('venue', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'seeking_description')
    op.drop_column('venue', 'seeking_talent')
    op.drop_column('venue', 'website')
    op.drop_column('artist', 'seeking_description')
    op.drop_column('artist', 'seeking_venue')
    # ### end Alembic commands ###