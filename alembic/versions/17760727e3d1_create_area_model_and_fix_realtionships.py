"""Create Area model and fix realtionships

Revision ID: 17760727e3d1
Revises: ef6c8e78a7a7
Create Date: 2020-07-16 17:53:59.615639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17760727e3d1'
down_revision = 'ef6c8e78a7a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('areas',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column('events', sa.Column('area_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'events', 'areas', ['area_id'], ['id'])
    op.drop_column('events', 'area')
    op.add_column('houses', sa.Column('area_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'houses', 'areas', ['area_id'], ['id'])
    op.drop_column('houses', 'area')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('houses', sa.Column('area', sa.VARCHAR(),
                                      autoincrement=False, nullable=True))
    op.drop_constraint(None, 'houses', type_='foreignkey')
    op.drop_column('houses', 'area_id')
    op.add_column('events', sa.Column('area', sa.VARCHAR(),
                                      autoincrement=False, nullable=True))
    op.drop_constraint(None, 'events', type_='foreignkey')
    op.drop_column('events', 'area_id')
    op.drop_table('areas')
    # ### end Alembic commands ###
