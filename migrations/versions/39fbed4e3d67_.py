"""empty message

Revision ID: 39fbed4e3d67
Revises: 1a455fa252a7
Create Date: 2024-06-13 16:05:45.296721

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39fbed4e3d67'
down_revision = '1a455fa252a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website_link', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('currently_seeking', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('seeking_content', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.drop_column('seeking_content')
        batch_op.drop_column('currently_seeking')
        batch_op.drop_column('website_link')

    op.drop_table('Show')
    # ### end Alembic commands ###
