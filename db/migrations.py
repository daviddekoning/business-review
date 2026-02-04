"""Database migrations system.

Handles schema version tracking and upgrades.
"""

import sqlite3
from db import get_db


def get_schema_version(conn: sqlite3.Connection) -> int:
    """Get current schema version from database."""
    try:
        cursor = conn.execute("SELECT version FROM schema_version")
        row = cursor.fetchone()
        return row["version"] if row else 0
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return 0


def set_schema_version(conn: sqlite3.Connection, version: int) -> None:
    """Set the schema version."""
    conn.execute(
        """INSERT INTO schema_version (id, version) VALUES (1, ?)
           ON CONFLICT(id) DO UPDATE SET version = ?""",
        (version, version),
    )
    conn.commit()


# Migration functions - each takes a connection and applies changes
def migration_001_add_analysis_name(conn: sqlite3.Connection) -> None:
    """Add name column to analyses and remove unique constraint."""
    # Check if name column already exists
    cursor = conn.execute("PRAGMA table_info(analyses)")
    columns = [row["name"] for row in cursor.fetchall()]

    if "name" in columns:
        return  # Already migrated

    # SQLite doesn't support DROP CONSTRAINT, so we need to recreate the table
    conn.executescript("""
        -- Create new table with updated schema
        CREATE TABLE analyses_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            template_type TEXT NOT NULL,
            data_json TEXT NOT NULL DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
        );
        
        -- Copy existing data, using template_type as default name
        INSERT INTO analyses_new (id, business_id, name, template_type, data_json, created_at, updated_at)
        SELECT id, business_id, 
               CASE template_type
                   WHEN 'pestel' THEN 'PESTEL Analysis'
                   WHEN 'five_forces' THEN 'Five Forces Analysis'
                   WHEN 'vrio' THEN 'VRIO Analysis'
                   WHEN 'wardley' THEN 'Wardley Map'
                   ELSE template_type
               END as name,
               template_type, data_json, created_at, updated_at
        FROM analyses;
        
        -- Drop old table and rename new one
        DROP TABLE analyses;
        ALTER TABLE analyses_new RENAME TO analyses;
        
        -- Recreate index
        CREATE INDEX IF NOT EXISTS idx_analyses_business ON analyses(business_id);
    """)


# List of all migrations in order
MIGRATIONS = [
    (1, migration_001_add_analysis_name),
]


def run_migrations() -> None:
    """Run all pending migrations."""
    conn = get_db()

    # Ensure schema_version table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            id INTEGER PRIMARY KEY,
            version INTEGER NOT NULL
        )
    """)
    conn.commit()

    current_version = get_schema_version(conn)

    for version, migration_func in MIGRATIONS:
        if version > current_version:
            print(f"Running migration {version}: {migration_func.__name__}")
            migration_func(conn)
            set_schema_version(conn, version)
            print(f"Migration {version} complete")

    conn.close()


if __name__ == "__main__":
    run_migrations()
