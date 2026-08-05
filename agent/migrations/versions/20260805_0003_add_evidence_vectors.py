"""Add persistent evidence vectors with pgvector support."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import UserDefinedType


revision = "20260805_0003"
down_revision = "20260805_0002"
branch_labels = None
depends_on = None


class Vector384(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw):
        return "vector(384)"


def upgrade() -> None:
    dialect = op.get_bind().dialect.name
    if dialect == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
        embedding_type = Vector384()
        metadata_type = postgresql.JSONB(astext_type=sa.Text())
    else:
        embedding_type = sa.Text()
        metadata_type = sa.JSON()

    op.create_table(
        "evidence_vectors",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("owner_id", sa.String(255), nullable=True, index=True),
        sa.Column("run_id", sa.String(36), nullable=True, index=True),
        sa.Column("scope", sa.String(20), nullable=False, index=True),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_id", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", metadata_type, nullable=False),
        sa.Column("embedding", embedding_type, nullable=False),
    )
    if dialect == "postgresql":
        op.execute(
            "CREATE INDEX ix_evidence_vectors_embedding_hnsw "
            "ON evidence_vectors USING hnsw (embedding vector_cosine_ops)"
        )


def downgrade() -> None:
    op.drop_table("evidence_vectors")
