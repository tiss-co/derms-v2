"""empty message

Revision ID: f4cd9a88f321
Revises: 7796538b99d3
Create Date: 2022-08-13 17:25:15.869537

"""
from alembic import op
import sqlalchemy as sa

# (help: https://alembic.sqlalchemy.org/en/latest/autogenerate.html#controlling-the-module-prefix)
# (help: https://stackoverflow.com/a/34294464)
import backend

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f4cd9a88f321'
down_revision = '7796538b99d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_uuid', table_name='users')
    op.drop_table('users')
    op.add_column('activations', sa.Column('manual', sa.Boolean(), server_default='false', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('activations', 'manual')
    op.create_table('users',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('uuid', postgresql.UUID(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('first_name', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('last_name', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('username', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('admin', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('active', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('authenticated', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('confirmed_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='pk_users')
    )
    op.create_index('ix_users_uuid', 'users', ['uuid'], unique=False)
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    # ### end Alembic commands ###
