"""Initial SaaS schema

Revision ID: 001
Revises:
Create Date: 2026-06-06

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tenants table
    op.create_table('tenants',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('tier', sa.String(50), default='free'),
        sa.Column('max_monthly_tokens', sa.Integer(), default=100000),
        sa.Column('max_concurrent_requests', sa.Integer(), default=5),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('stripe_customer_id')
    )
    op.create_index('ix_tenants_created_at', 'tenants', ['created_at'])

    # Users table
    op.create_table('users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), default='user'),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('ix_users_email', 'users', ['email'])

    # API Keys table
    op.create_table('api_keys',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('key', sa.String(64), nullable=False),
        sa.Column('secret_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.UniqueConstraint('key')
    )
    op.create_index('ix_api_keys_tenant_id', 'api_keys', ['tenant_id'])

    # Chat Sessions table
    op.create_table('chat_sessions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('knowledge_base_id', sa.String(36), nullable=True),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('title', sa.String(500), default='New Chat'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('total_tokens_used', sa.Integer(), default=0),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_chat_sessions_tenant_id', 'chat_sessions', ['tenant_id'])
    op.create_index('ix_chat_sessions_created_at', 'chat_sessions', ['created_at'])

    # Chat Messages table
    op.create_table('chat_messages',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('session_id', sa.String(36), nullable=False),
        sa.Column('role', sa.String(10), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), default=0),
        sa.Column('completion_tokens', sa.Integer(), default=0),
        sa.Column('sources', sa.Text(), default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'])
    )
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'])
    op.create_index('ix_chat_messages_created_at', 'chat_messages', ['created_at'])

    # Usage Metrics table
    op.create_table('usage_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('chat_sessions', sa.Integer(), default=0),
        sa.Column('total_prompt_tokens', sa.Integer(), default=0),
        sa.Column('total_completion_tokens', sa.Integer(), default=0),
        sa.Column('total_inference_ms', sa.Integer(), default=0),
        sa.Column('gpu_seconds_used', sa.Float(), default=0),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'])
    )
    op.create_index('ix_usage_metrics_tenant_id', 'usage_metrics', ['tenant_id'])
    op.create_index('ix_usage_metrics_date', 'usage_metrics', ['date'])


def downgrade() -> None:
    op.drop_table('usage_metrics')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('api_keys')
    op.drop_table('users')
    op.drop_table('tenants')
