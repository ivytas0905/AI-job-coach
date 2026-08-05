from pathlib import Path
import sqlite3

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


PROJECT_ROOT = Path(__file__).parents[2]


def upgrade(database_path: Path) -> None:
    config = Config(PROJECT_ROOT / "alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.as_posix()}")
    command.upgrade(config, "head")


def downgrade(database_path: Path) -> None:
    config = Config(PROJECT_ROOT / "alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.as_posix()}")
    command.downgrade(config, "base")


def test_fresh_database_upgrades_to_workflow_schema(tmp_path):
    database_path = tmp_path / "fresh.db"

    upgrade(database_path)

    tables = set(inspect(create_engine(f"sqlite:///{database_path}")).get_table_names())
    assert {
        "tailoring_runs",
        "agent_messages",
        "proposals",
        "proposal_decisions",
        "resume_versions",
        "exports",
        "evidence_vectors",
    } <= tables


def test_prior_schema_upgrades_without_losing_master_resume(tmp_path):
    database_path = tmp_path / "prior.db"
    connection = sqlite3.connect(database_path)
    connection.execute(
        "CREATE TABLE master_resumes ("
        "id VARCHAR(36) PRIMARY KEY, user_id VARCHAR(255) NOT NULL, "
        "filename VARCHAR(255) NOT NULL, parsed_data JSON NOT NULL)"
    )
    connection.execute(
        "INSERT INTO master_resumes VALUES (?, ?, ?, ?)",
        ("master-old", "user-a", "old.pdf", '{}'),
    )
    connection.execute(
        "CREATE TABLE resume_versions ("
        "id VARCHAR(36) PRIMARY KEY, master_resume_id VARCHAR(36) NOT NULL, "
        "version_name VARCHAR(255) NOT NULL, content JSON NOT NULL)"
    )
    connection.execute(
        "INSERT INTO resume_versions VALUES (?, ?, ?, ?)",
        ("version-old", "master-old", "Old version", '{}'),
    )
    connection.commit()
    connection.close()

    upgrade(database_path)

    engine = create_engine(f"sqlite:///{database_path}")
    with engine.connect() as upgraded:
        assert upgraded.execute(
            text("SELECT filename FROM master_resumes WHERE id='master-old'")
        ).scalar_one() == "old.pdf"
        assert upgraded.execute(
            text("SELECT version_name FROM resume_versions WHERE id='version-old'")
        ).scalar_one() == "Old version"
    assert "tailoring_runs" in inspect(engine).get_table_names()
    assert {"user_id", "run_id", "parent_version_id", "version_number"} <= {
        column["name"] for column in inspect(engine).get_columns("resume_versions")
    }


def test_downgrade_removes_workflow_schema_but_preserves_legacy_tables(tmp_path):
    database_path = tmp_path / "downgrade.db"
    upgrade(database_path)

    downgrade(database_path)

    inspector = inspect(create_engine(f"sqlite:///{database_path}"))
    assert "master_resumes" in inspector.get_table_names()
    assert "tailoring_runs" not in inspector.get_table_names()
    assert "run_id" not in {
        column["name"] for column in inspector.get_columns("resume_versions")
    }
