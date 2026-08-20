"""initial schema"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("monitors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("method", sa.String(10), nullable=False, server_default="GET"),
        sa.Column("headers", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("body", sa.Text()),
        sa.Column("expected_status", sa.Integer(), nullable=False, server_default="200"),
        sa.Column("expected_text", sa.String(500)),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("interval_seconds", sa.Integer(), nullable=False, server_default="300"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_checked_at", sa.DateTime(timezone=True)),
        sa.Column("next_check_at", sa.DateTime(timezone=True)),
        sa.Column("current_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table("checks",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("monitor_id", sa.Integer(), sa.ForeignKey("monitors.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("status_code", sa.Integer()),
        sa.Column("response_time_ms", sa.Integer()),
        sa.Column("error", sa.Text()),
        sa.Column("response_excerpt", sa.Text()),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
    )
    op.create_table("incidents",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("monitor_id", sa.Integer(), sa.ForeignKey("monitors.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("check_id", sa.BigInteger(), sa.ForeignKey("checks.id", ondelete="SET NULL")),
        sa.Column("state", sa.String(20), nullable=False, server_default="open"),
        sa.Column("title", sa.String(250), nullable=False),
        sa.Column("cause", sa.Text()),
        sa.Column("recommendations", sa.Text()),
        sa.Column("raw_analysis", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
    )

def downgrade():
    op.drop_table("incidents"); op.drop_table("checks"); op.drop_table("monitors")

