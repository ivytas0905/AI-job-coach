"""Adopt normalized workflow persistence.

Revision ID: 20260805_0001
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = "20260805_0001"
down_revision = None
branch_labels = None
depends_on = None


VERSION_COLUMNS = {
    "user_id": sa.Column("user_id", sa.String(255), nullable=True),
    "run_id": sa.Column("run_id", sa.String(36), nullable=True),
    "parent_version_id": sa.Column("parent_version_id", sa.String(36), nullable=True),
    "version_number": sa.Column("version_number", sa.Integer(), nullable=True),
}


def schema_snapshot() -> sa.MetaData:
    """Return the schema frozen at this revision; never import live ORM metadata."""
    metadata = sa.MetaData()
    sa.Table(
        "master_resumes",
        metadata,
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.Text()),
        sa.Column("parsed_data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime()),
    )
    sa.Table(
        "jd_analyses",
        metadata,
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column("company", sa.String(255), index=True),
        sa.Column("job_title", sa.String(255), nullable=False, index=True),
        sa.Column("job_url", sa.Text()),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("jd_hash", sa.String(64), unique=True, index=True),
        sa.Column("analysis_result", sa.JSON(), nullable=False),
        sa.Column("analyzed_at", sa.DateTime(), nullable=False),
    )
    sa.Table(
        "tailoring_runs",
        metadata,
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column("master_resume_id", sa.String(36), sa.ForeignKey("master_resumes.id")),
        sa.Column("jd_analysis_id", sa.String(36), sa.ForeignKey("jd_analyses.id")),
        sa.Column("state", sa.String(50), nullable=False),
        sa.Column("provider", sa.String(100), nullable=False),
        sa.Column("model", sa.String(255), nullable=False),
        sa.Column("current_version_id", sa.String(36)),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime()),
    )
    sa.Table(
        "resume_versions",
        metadata,
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(255), index=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("tailoring_runs.id"), index=True),
        sa.Column("master_resume_id", sa.String(36), sa.ForeignKey("master_resumes.id"), nullable=False, index=True),
        sa.Column("parent_version_id", sa.String(36), sa.ForeignKey("resume_versions.id")),
        sa.Column("version_number", sa.Integer()),
        sa.Column("version_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("company", sa.String(255), index=True),
        sa.Column("job_title", sa.String(255), index=True),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("target_keywords", sa.JSON()),
        sa.Column("jd_analysis_id", sa.String(36), sa.ForeignKey("jd_analyses.id")),
        sa.Column("ats_score", sa.Integer()),
        sa.Column("keyword_match_score", sa.Float()),
        sa.Column("status", sa.String(50)),
        sa.Column("applied_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime()),
    )
    sa.Table(
        "chat_sessions",
        metadata,
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column("resume_version_id", sa.String(36), sa.ForeignKey("resume_versions.id"), index=True),
        sa.Column("session_name", sa.String(255)),
        sa.Column("messages", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("last_activity_at", sa.DateTime()),
    )
    sa.Table(
        "optimization_history",
        metadata,
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("resume_version_id", sa.String(36), sa.ForeignKey("resume_versions.id"), nullable=False, index=True),
        sa.Column("section", sa.String(50)),
        sa.Column("item_index", sa.Integer()),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("optimized_text", sa.Text(), nullable=False),
        sa.Column("optimization_type", sa.String(50)),
        sa.Column("improvements", sa.JSON()),
        sa.Column("target_keywords", sa.JSON()),
        sa.Column("user_action", sa.String(20)),
        sa.Column("modified_text", sa.Text()),
        sa.Column("suggested_at", sa.DateTime(), nullable=False),
        sa.Column("actioned_at", sa.DateTime()),
    )
    sa.Table(
        "agent_messages",
        metadata,
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("tailoring_runs.id"), nullable=False, index=True),
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("run_id", "sequence", name="uq_message_run_sequence"),
    )
    sa.Table(
        "proposals",
        metadata,
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("tailoring_runs.id"), nullable=False, index=True),
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("suggested_text", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("source_evidence", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    sa.Table(
        "proposal_decisions",
        metadata,
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("proposal_id", sa.String(36), sa.ForeignKey("proposals.id"), nullable=False, index=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("tailoring_runs.id"), nullable=False, index=True),
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column("proposal_revision", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("run_id", "idempotency_key", name="uq_decision_run_idempotency"),
        sa.UniqueConstraint("proposal_id", "proposal_revision", name="uq_decision_proposal_revision"),
    )
    sa.Table(
        "exports",
        metadata,
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("tailoring_runs.id"), nullable=False, index=True),
        sa.Column("version_id", sa.String(36), sa.ForeignKey("resume_versions.id"), nullable=False, index=True),
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column("storage_key", sa.Text(), nullable=False, unique=True),
        sa.Column("content_type", sa.String(255), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    return metadata


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())
    prior_version_columns = (
        {column["name"] for column in inspector.get_columns("resume_versions")}
        if "resume_versions" in existing_tables
        else set()
    )

    schema_snapshot().create_all(bind=bind)

    if "resume_versions" in existing_tables:
        existing_indexes = {
            index["name"] for index in inspector.get_indexes("resume_versions")
        }
        for name, column in VERSION_COLUMNS.items():
            if name not in prior_version_columns:
                op.add_column("resume_versions", column)
        if "ix_resume_versions_user_id" not in existing_indexes:
            op.create_index(
                "ix_resume_versions_user_id",
                "resume_versions",
                ["user_id"],
                unique=False,
            )
        if "ix_resume_versions_run_id" not in existing_indexes:
            op.create_index(
                "ix_resume_versions_run_id",
                "resume_versions",
                ["run_id"],
                unique=False,
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "exports" in tables:
        op.drop_table("exports")
    if "resume_versions" in tables:
        version_columns = {
            column["name"] for column in inspector.get_columns("resume_versions")
        }
        version_indexes = {
            index["name"] for index in inspector.get_indexes("resume_versions")
        }
        if bind.dialect.name != "sqlite":
            for foreign_key in inspector.get_foreign_keys("resume_versions"):
                if set(foreign_key["constrained_columns"]) & {
                    "run_id",
                    "parent_version_id",
                } and foreign_key["name"]:
                    op.drop_constraint(
                        foreign_key["name"], "resume_versions", type_="foreignkey"
                    )
        with op.batch_alter_table("resume_versions") as batch:
            for index_name in (
                "ix_resume_versions_run_id",
                "ix_resume_versions_user_id",
            ):
                if index_name in version_indexes:
                    batch.drop_index(index_name)
            for column_name in (
                "version_number",
                "parent_version_id",
                "run_id",
                "user_id",
            ):
                if column_name in version_columns:
                    batch.drop_column(column_name)
    for table in (
        "proposal_decisions",
        "proposals",
        "agent_messages",
        "tailoring_runs",
    ):
        if table in tables:
            op.drop_table(table)
