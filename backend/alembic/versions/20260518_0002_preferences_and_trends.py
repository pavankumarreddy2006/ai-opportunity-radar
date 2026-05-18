"""add preferences and trend scores"""

from alembic import op
import sqlalchemy as sa


revision = "20260518_0002"
down_revision = "20260517_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("digest_frequency", sa.String(length=40), nullable=False, server_default="daily"),
        sa.Column("minimum_importance_score", sa.Integer(), nullable=False, server_default="55"),
        sa.Column("minimum_opportunity_score", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("enable_weekly_report", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("enable_email_digest", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("source_weights", sa.JSON(), nullable=False),
        sa.Column("interest_weights", sa.JSON(), nullable=False),
        sa.Column("exploration_rate", sa.Float(), nullable=False, server_default="0.15"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_preferences_user_id", "user_preferences", ["user_id"], unique=True)

    op.create_table(
        "trend_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("raw_news_id", sa.Integer(), sa.ForeignKey("raw_news.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scored_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("trend_velocity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("engagement_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("freshness_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("reddit_activity_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("github_star_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("credibility_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("composite_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("factors", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("raw_news_id", "scored_at", name="uq_trend_score_raw_news_scored_at"),
    )
    op.create_index("ix_trend_scores_raw_news_id", "trend_scores", ["raw_news_id"], unique=False)
    op.create_index("ix_trend_scores_scored_at", "trend_scores", ["scored_at"], unique=False)
    op.create_index("ix_trend_scores_source", "trend_scores", ["source"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_trend_scores_source", table_name="trend_scores")
    op.drop_index("ix_trend_scores_scored_at", table_name="trend_scores")
    op.drop_index("ix_trend_scores_raw_news_id", table_name="trend_scores")
    op.drop_table("trend_scores")
    op.drop_index("ix_user_preferences_user_id", table_name="user_preferences")
    op.drop_table("user_preferences")
