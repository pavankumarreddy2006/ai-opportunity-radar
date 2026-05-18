"""add runtime query indexes"""

from alembic import op


revision = "20260518_0004"
down_revision = "20260518_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_signals_status_importance_created",
        "signals",
        ["status", "importance_score", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_signals_category_status_importance",
        "signals",
        ["category", "status", "importance_score"],
        unique=False,
    )
    op.create_index(
        "ix_raw_news_source_created",
        "raw_news",
        ["source", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_raw_news_source_created", table_name="raw_news")
    op.drop_index("ix_signals_category_status_importance", table_name="signals")
    op.drop_index("ix_signals_status_importance_created", table_name="signals")
