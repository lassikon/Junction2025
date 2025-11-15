"""add account system

Revision ID: 001_account_system
Revises: cee0f944a60e
Create Date: 2025-11-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001_account_system'
down_revision = 'cee0f944a60e'
branch_labels = None
depends_on = None


def upgrade():
    # Create accounts table
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('display_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('has_completed_onboarding', sa.Boolean(), nullable=False),
        sa.Column('default_age', sa.Integer(), nullable=True),
        sa.Column('default_city', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('default_education_path', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('default_risk_attitude', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('default_monthly_income', sa.Float(), nullable=True),
        sa.Column('default_monthly_expenses', sa.Float(), nullable=True),
        sa.Column('default_starting_savings', sa.Float(), nullable=True),
        sa.Column('default_starting_debt', sa.Float(), nullable=True),
        sa.Column('default_aspirations', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_accounts_username'), 'accounts', ['username'], unique=True)
    
    # Create session_tokens table
    op.create_table(
        'session_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_tokens_account_id'), 'session_tokens', ['account_id'], unique=False)
    op.create_index(op.f('ix_session_tokens_token'), 'session_tokens', ['token'], unique=True)
    
    # Add columns to player_profiles table
    with op.batch_alter_table('player_profiles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_test_mode', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.create_index(batch_op.f('ix_player_profiles_account_id'), ['account_id'], unique=False)
        batch_op.create_foreign_key('fk_player_profiles_account_id', 'accounts', ['account_id'], ['id'])
    
    # Add columns to leaderboard table
    with op.batch_alter_table('leaderboard', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_test_mode', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.create_index(batch_op.f('ix_leaderboard_account_id'), ['account_id'], unique=False)
        batch_op.create_foreign_key('fk_leaderboard_account_id', 'accounts', ['account_id'], ['id'])


def downgrade():
    # Remove columns from leaderboard table
    with op.batch_alter_table('leaderboard', schema=None) as batch_op:
        batch_op.drop_constraint('fk_leaderboard_account_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_leaderboard_account_id'))
        batch_op.drop_column('is_test_mode')
        batch_op.drop_column('account_id')
    
    # Remove columns from player_profiles table
    with op.batch_alter_table('player_profiles', schema=None) as batch_op:
        batch_op.drop_constraint('fk_player_profiles_account_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_player_profiles_account_id'))
        batch_op.drop_column('is_test_mode')
        batch_op.drop_column('account_id')
    
    # Drop session_tokens table
    op.drop_index(op.f('ix_session_tokens_token'), table_name='session_tokens')
    op.drop_index(op.f('ix_session_tokens_account_id'), table_name='session_tokens')
    op.drop_table('session_tokens')
    
    # Drop accounts table
    op.drop_index(op.f('ix_accounts_username'), table_name='accounts')
    op.drop_table('accounts')

