"""initial schema"""

from alembic import op
import sqlalchemy as sa


revision = "20260517_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "raw_news",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("link", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("engagement_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("summary_snippet", sa.Text(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("dedupe_key", sa.String(length=128), nullable=False),
        sa.Column("credibility_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("mention_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("dedupe_key", name="uq_raw_news_dedupe_key"),
    )
    op.create_index("ix_raw_news_dedupe_key", "raw_news", ["dedupe_key"], unique=False)
    op.create_index("ix_raw_news_published_at", "raw_news", ["published_at"], unique=False)
    op.create_index("ix_raw_news_source", "raw_news", ["source"], unique=False)
    op.create_index("ix_raw_news_title", "raw_news", ["title"], unique=False)

    op.create_table(
        "interests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "name", name="uq_user_interest_name"),
    )
    op.create_index("ix_interests_user_id", "interests", ["user_id"], unique=False)
    op.create_index("ix_interests_name", "interests", ["name"], unique=False)

    op.create_table(
        "signals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("raw_news_id", sa.Integer(), sa.ForeignKey("raw_news.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("importance_score", sa.Integer(), nullable=False),
        sa.Column("opportunity_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trend_velocity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("relevance_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("source_credibility", sa.Float(), nullable=False, server_default="0"),
        sa.Column("freshness_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("engagement_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("ranking_factors", sa.JSON(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="active"),
        sa.Column("action_recommendation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_signals_raw_news_id", "signals", ["raw_news_id"], unique=False)
    op.create_index("ix_signals_user_id", "signals", ["user_id"], unique=False)
    op.create_index("ix_signals_category", "signals", ["category"], unique=False)
    op.create_index("ix_signals_importance_score", "signals", ["importance_score"], unique=False)
    op.create_index("ix_signals_status", "signals", ["status"], unique=False)

    op.create_table(
        "summaries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("signal_id", sa.Integer(), sa.ForeignKey("signals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("headline", sa.Text(), nullable=False),
        sa.Column("what_happened", sa.Text(), nullable=False),
        sa.Column("why_it_matters", sa.Text(), nullable=False),
        sa.Column("why_you_should_care", sa.Text(), nullable=False),
        sa.Column("action_recommendation", sa.Text(), nullable=False),
        sa.Column("opportunity_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_summaries_signal_id", "summaries", ["signal_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_summaries_signal_id", table_name="summaries")
    op.drop_table("summaries")
    op.drop_index("ix_signals_status", table_name="signals")
    op.drop_index("ix_signals_importance_score", table_name="signals")
    op.drop_index("ix_signals_category", table_name="signals")
    op.drop_index("ix_signals_user_id", table_name="signals")
    op.drop_index("ix_signals_raw_news_id", table_name="signals")
    op.drop_table("signals")
    op.drop_index("ix_interests_name", table_name="interests")
    op.drop_index("ix_interests_user_id", table_name="interests")
    op.drop_table("interests")
    op.drop_index("ix_raw_news_title", table_name="raw_news")
    op.drop_index("ix_raw_news_source", table_name="raw_news")
    op.drop_index("ix_raw_news_published_at", table_name="raw_news")
    op.drop_index("ix_raw_news_dedupe_key", table_name="raw_news")
    op.drop_table("raw_news")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
