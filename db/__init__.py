"""Database connection and initialization."""
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "data" / "business_analysis.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_db() -> sqlite3.Connection:
    """Get a database connection with row factory enabled."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Initialize the database with the schema."""
    conn = get_db()
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.close()


def dict_from_row(row: sqlite3.Row | None) -> dict | None:
    """Convert a sqlite3.Row to a dictionary."""
    if row is None:
        return None
    return dict(row)
