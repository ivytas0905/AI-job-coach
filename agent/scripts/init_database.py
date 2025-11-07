"""
Database Initialization Script

This script initializes the database tables for the AI Job Coach application.

Usage:
    python scripts/init_database.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to Python path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agent_service.config import get_settings
from agent_service.infra.storage.database import DatabaseManager
from agent_service.infra.storage.models import (
    MasterResumeModel,
    ResumeVersionModel,
    JDAnalysisModel,
    ChatSessionModel,
    OptimizationHistoryModel
)


async def init_database():
    """Initialize database and create all tables."""

    print("=" * 60)
    print("AI Job Coach - Database Initialization")
    print("=" * 60)
    print()

    # Load settings
    settings = get_settings()

    print(f"Environment: {settings.environment}")
    print(f"Database URL: {settings.database_url}")
    print()

    # Create database manager
    db_manager = DatabaseManager(
        database_url=settings.database_url,
        echo=settings.database_echo
    )

    try:
        print("Creating database tables...")
        await db_manager.create_tables()
        print("✅ Database tables created successfully!")
        print()

        # List created tables
        print("Created tables:")
        print("  - master_resumes")
        print("  - resume_versions")
        print("  - jd_analyses")
        print("  - chat_sessions")
        print("  - optimization_history")
        print()

        print("=" * 60)
        print("✅ Database initialization complete!")
        print("=" * 60)

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Database initialization failed!")
        print(f"Error: {e}")
        print("=" * 60)
        raise

    finally:
        await db_manager.close()


async def drop_and_recreate():
    """Drop all tables and recreate them. WARNING: This deletes all data!"""

    print("=" * 60)
    print("⚠️  WARNING: This will DELETE ALL DATA!")
    print("=" * 60)

    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() != 'yes':
        print("Aborted.")
        return

    settings = get_settings()
    db_manager = DatabaseManager(
        database_url=settings.database_url,
        echo=settings.database_echo
    )

    try:
        print()
        print("Dropping all tables...")
        await db_manager.drop_tables()
        print("✅ All tables dropped")
        print()

        print("Creating tables...")
        await db_manager.create_tables()
        print("✅ Tables created")
        print()

        print("=" * 60)
        print("✅ Database reset complete!")
        print("=" * 60)

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Database reset failed!")
        print(f"Error: {e}")
        print("=" * 60)
        raise

    finally:
        await db_manager.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize database")
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Drop all tables and recreate (WARNING: deletes all data)'
    )

    args = parser.parse_args()

    if args.reset:
        asyncio.run(drop_and_recreate())
    else:
        asyncio.run(init_database())
