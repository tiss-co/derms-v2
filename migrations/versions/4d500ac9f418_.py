"""empty message

Revision ID: 4d500ac9f418
Revises: 092418c0e1fd
Create Date: 2022-08-30 13:09:15.004628

"""
from alembic import op
import sqlalchemy as sa

# (help: https://alembic.sqlalchemy.org/en/latest/autogenerate.html#controlling-the-module-prefix)
# (help: https://stackoverflow.com/a/34294464)
import backend



# revision identifiers, used by Alembic.
revision = '4d500ac9f418'
down_revision = '092418c0e1fd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('battery_details',
    sa.Column('id', sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('uuid', backend.database.types.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('datetime', sa.DateTime(), nullable=False),
    sa.Column('current_status', sa.String(), nullable=True),
    sa.Column('p_max', sa.Float(), nullable=True),
    sa.Column('p_max_charge', sa.Float(), nullable=True),
    sa.Column('capacity', sa.Float(), nullable=True),
    sa.Column('available_energy', sa.Float(), nullable=True),
    sa.Column('state_of_charge', sa.Float(), nullable=True),
    sa.Column('remaining_life_cycle', sa.Float(), nullable=True),
    sa.Column('state_of_health', sa.Float(), nullable=True),
    sa.Column('grid_frequency', sa.Float(), nullable=True),
    sa.Column('average_grid_current', sa.Float(), nullable=True),
    sa.Column('reactive_power', sa.Float(), nullable=True),
    sa.Column('ambient_temperature', sa.Float(), nullable=True),
    sa.Column('power_factor', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_battery_details'))
    )
    op.create_index(op.f('ix_battery_details_datetime'), 'battery_details', ['datetime'], unique=True)
    op.create_index(op.f('ix_battery_details_uuid'), 'battery_details', ['uuid'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_battery_details_uuid'), table_name='battery_details')
    op.drop_index(op.f('ix_battery_details_datetime'), table_name='battery_details')
    op.drop_table('battery_details')
    # ### end Alembic commands ###
