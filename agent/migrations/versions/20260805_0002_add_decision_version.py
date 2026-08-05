"""Link accepted proposal decisions to their created version."""

from alembic import op
import sqlalchemy as sa

revision = "20260805_0002"
down_revision = "20260805_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("proposal_decisions") as batch:
        batch.add_column(sa.Column("version_id", sa.String(36), nullable=True))
        batch.create_foreign_key(
            "fk_proposal_decisions_version_id", "resume_versions", ["version_id"], ["id"]
        )
    op.create_table(
        "agent_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("tailoring_runs.id"), nullable=False, index=True),
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("run_id", "sequence", name="uq_event_run_sequence"),
    )


def downgrade() -> None:
    op.drop_table("agent_events")
    with op.batch_alter_table("proposal_decisions") as batch:
        batch.drop_constraint("fk_proposal_decisions_version_id", type_="foreignkey")
        batch.drop_column("version_id")
