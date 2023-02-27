"""empty message

Revision ID: 7796538b99d3
Revises: f36f10d9bf9c
Create Date: 2022-07-25 08:44:45.992430

"""
from alembic import op
import sqlalchemy as sa

# (help: https://alembic.sqlalchemy.org/en/latest/autogenerate.html#controlling-the-module-prefix)
# (help: https://stackoverflow.com/a/34294464)
import backend



# revision identifiers, used by Alembic.
revision = '7796538b99d3'
down_revision = 'f36f10d9bf9c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('power_quality',
    sa.Column('id', sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('uuid', backend.database.types.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('datetime', sa.DateTime(), nullable=False),
    sa.Column('voltage_utility', sa.Float(), nullable=True),
    sa.Column('voltage_battery', sa.Float(), nullable=True),
    sa.Column('voltage_facility', sa.Float(), nullable=True),
    sa.Column('current_utility', sa.Float(), nullable=True),
    sa.Column('current_battery', sa.Float(), nullable=True),
    sa.Column('current_facility', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_power_quality'))
    )
    op.create_index(op.f('ix_power_quality_datetime'), 'power_quality', ['datetime'], unique=True)
    op.create_index(op.f('ix_power_quality_uuid'), 'power_quality', ['uuid'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_power_quality_uuid'), table_name='power_quality')
    op.drop_index(op.f('ix_power_quality_datetime'), table_name='power_quality')
    op.drop_table('power_quality')
    # ### end Alembic commands ###
