"""add canonical news source and category tables"""

from alembic import op
import sqlalchemy as sa


revision = "20260518_0003"
down_revision = "20260518_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("source_type", sa.String(length=60), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("credibility_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", name="uq_sources_name"),
    )
    op.create_index("ix_sources_name", "sources", ["name"], unique=False)
    op.create_index("ix_sources_source_type", "sources", ["source_type"], unique=False)
    op.create_index("ix_sources_is_active", "sources", ["is_active"], unique=False)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", name="uq_categories_name"),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=False)

    op.create_table(
        "news",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source", sa.String(length=120), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("importance_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("category", sa.String(length=100), nullable=False, server_default="general"),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("url", name="uq_news_url"),
    )
    op.create_index("ix_news_title", "news", ["title"], unique=False)
    op.create_index("ix_news_source", "news", ["source"], unique=False)
    op.create_index("ix_news_published_at", "news", ["published_at"], unique=False)
    op.create_index("ix_news_importance_score", "news", ["importance_score"], unique=False)
    op.create_index("ix_news_category", "news", ["category"], unique=False)
    op.create_index("ix_news_source_id", "news", ["source_id"], unique=False)
    op.create_index("ix_news_category_id", "news", ["category_id"], unique=False)

    with op.batch_alter_table("summaries") as batch_op:
        batch_op.add_column(sa.Column("news_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_summaries_news_id_news",
            "news",
            ["news_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_index("ix_summaries_news_id", ["news_id"], unique=False)
        batch_op.alter_column("signal_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("summaries") as batch_op:
        batch_op.alter_column("signal_id", existing_type=sa.Integer(), nullable=False)
        batch_op.drop_index("ix_summaries_news_id")
        batch_op.drop_constraint("fk_summaries_news_id_news", type_="foreignkey")
        batch_op.drop_column("news_id")

    op.drop_index("ix_news_category_id", table_name="news")
    op.drop_index("ix_news_source_id", table_name="news")
    op.drop_index("ix_news_category", table_name="news")
    op.drop_index("ix_news_importance_score", table_name="news")
    op.drop_index("ix_news_published_at", table_name="news")
    op.drop_index("ix_news_source", table_name="news")
    op.drop_index("ix_news_title", table_name="news")
    op.drop_table("news")

    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")

    op.drop_index("ix_sources_is_active", table_name="sources")
    op.drop_index("ix_sources_source_type", table_name="sources")
    op.drop_index("ix_sources_name", table_name="sources")
    op.drop_table("sources")
