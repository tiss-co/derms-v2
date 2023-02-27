"""empty message

Revision ID: 178065f3a56d
Revises: 
Create Date: 2022-01-27 06:35:14.336721

"""
from alembic import op
import sqlalchemy as sa

# (help: https://alembic.sqlalchemy.org/en/latest/autogenerate.html#controlling-the-module-prefix)
# (help: https://stackoverflow.com/a/34294464)
import backend



# revision identifiers, used by Alembic.
revision = '178065f3a56d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('activations',
    sa.Column('id', sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('uuid', backend.database.types.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('last_update', sa.DateTime(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('start', sa.Integer(), nullable=True),
    sa.Column('end', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_activations'))
    )
    op.create_index(op.f('ix_activations_date'), 'activations', ['date'], unique=False)
    op.create_index(op.f('ix_activations_uuid'), 'activations', ['uuid'], unique=False)
    op.create_table('loads',
    sa.Column('id', sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('uuid', backend.database.types.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('datetime', sa.DateTime(), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_loads'))
    )
    op.create_index(op.f('ix_loads_datetime'), 'loads', ['datetime'], unique=False)
    op.create_index(op.f('ix_loads_uuid'), 'loads', ['uuid'], unique=False)
    op.create_table('results',
    sa.Column('id', sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('uuid', backend.database.types.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('datetime', sa.DateTime(), nullable=False),
    sa.Column('charging_status', sa.Integer(), nullable=False),
    sa.Column('charging_mode', sa.Integer(), nullable=False),
    sa.Column('power', sa.Float(), nullable=False),
    sa.Column('limited_soc', sa.Float(), nullable=False),
    sa.Column('real_soc', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_results'))
    )
    op.create_index(op.f('ix_results_datetime'), 'results', ['datetime'], unique=False)
    op.create_index(op.f('ix_results_uuid'), 'results', ['uuid'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('uuid', backend.database.types.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('first_name', sa.String(length=32), nullable=False),
    sa.Column('last_name', sa.String(length=32), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=False),
    sa.Column('email', sa.String(length=32), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('admin', sa.Boolean(name='admin'), server_default='false', nullable=False),
    sa.Column('active', sa.Boolean(name='active'), server_default='false', nullable=False),
    sa.Column('authenticated', sa.Boolean(name='authenticated'), server_default='false', nullable=False),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_uuid'), 'users', ['uuid'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_uuid'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_results_uuid'), table_name='results')
    op.drop_index(op.f('ix_results_datetime'), table_name='results')
    op.drop_table('results')
    op.drop_index(op.f('ix_loads_uuid'), table_name='loads')
    op.drop_index(op.f('ix_loads_datetime'), table_name='loads')
    op.drop_table('loads')
    op.drop_index(op.f('ix_activations_uuid'), table_name='activations')
    op.drop_index(op.f('ix_activations_date'), table_name='activations')
    op.drop_table('activations')
    # ### end Alembic commands ###
