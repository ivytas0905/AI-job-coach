"""Add idempotency keys for restore and export commands."""

from alembic import op
import sqlalchemy as sa

revision = "20260805_0004"
down_revision = "20260805_0003"
branch_labels = None
depends_on = None

def upgrade() -> None:
    with op.batch_alter_table("proposals") as batch:
        batch.add_column(sa.Column("evidence_request", sa.Text(), nullable=True))
    with op.batch_alter_table("resume_versions") as batch:
        batch.add_column(sa.Column("idempotency_key", sa.String(255), nullable=True))
        batch.create_unique_constraint("uq_version_run_idempotency", ["run_id", "idempotency_key"])
    with op.batch_alter_table("exports") as batch:
        batch.add_column(sa.Column("idempotency_key", sa.String(255), nullable=True))
        batch.create_unique_constraint("uq_export_run_idempotency", ["run_id", "idempotency_key"])

def downgrade() -> None:
    with op.batch_alter_table("exports") as batch:
        batch.drop_constraint("uq_export_run_idempotency", type_="unique")
        batch.drop_column("idempotency_key")
    with op.batch_alter_table("resume_versions") as batch:
        batch.drop_constraint("uq_version_run_idempotency", type_="unique")
        batch.drop_column("idempotency_key")
    with op.batch_alter_table("proposals") as batch:
        batch.drop_column("evidence_request")
