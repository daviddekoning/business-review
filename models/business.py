"""Business model - CRUD operations for businesses."""

from db import get_db, dict_from_row


BUSINESS_TYPES = ["product", "company", "business_unit"]


def get_all() -> list[dict]:
    """Get all businesses."""
    conn = get_db()
    cursor = conn.execute("SELECT * FROM businesses ORDER BY updated_at DESC")
    businesses = [dict_from_row(row) for row in cursor.fetchall()]
    conn.close()
    return businesses


def get_by_id(business_id: int) -> dict | None:
    """Get a business by ID."""
    conn = get_db()
    cursor = conn.execute("SELECT * FROM businesses WHERE id = ?", (business_id,))
    business = dict_from_row(cursor.fetchone())
    conn.close()
    return business


def create(
    name: str, description: str, business_type: str, strategic_question: str
) -> int:
    """Create a new business. Returns the new business ID."""
    if business_type not in BUSINESS_TYPES:
        raise ValueError(f"Invalid business type: {business_type}")

    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO businesses (name, description, type, strategic_question)
           VALUES (?, ?, ?, ?)""",
        (name, description, business_type, strategic_question),
    )
    conn.commit()
    business_id = cursor.lastrowid
    conn.close()
    return business_id


def update(
    business_id: int,
    name: str,
    description: str,
    business_type: str,
    strategic_question: str,
) -> bool:
    """Update a business. Returns True if successful."""
    if business_type not in BUSINESS_TYPES:
        raise ValueError(f"Invalid business type: {business_type}")

    conn = get_db()
    cursor = conn.execute(
        """UPDATE businesses 
           SET name = ?, description = ?, type = ?, strategic_question = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ?""",
        (name, description, business_type, strategic_question, business_id),
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete(business_id: int) -> bool:
    """Delete a business. Returns True if successful."""
    conn = get_db()
    cursor = conn.execute("DELETE FROM businesses WHERE id = ?", (business_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success
