"""Research model - CRUD operations for research items and quotes."""

from pathlib import Path
from db import get_db, dict_from_row

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
ITEM_TYPES = ["article", "note", "interview", "document", "other"]


def ensure_upload_dir(business_id: int) -> Path:
    """Ensure upload directory exists for a business."""
    path = UPLOAD_DIR / str(business_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


# --- Research Items ---


def get_items_for_business(business_id: int) -> list[dict]:
    """Get all research items for a business."""
    conn = get_db()
    cursor = conn.execute(
        "SELECT * FROM research_items WHERE business_id = ? ORDER BY created_at DESC",
        (business_id,),
    )
    items = [dict_from_row(row) for row in cursor.fetchall()]
    conn.close()
    return items


def get_item_by_id(item_id: int) -> dict | None:
    """Get a research item by ID."""
    conn = get_db()
    cursor = conn.execute("SELECT * FROM research_items WHERE id = ?", (item_id,))
    item = dict_from_row(cursor.fetchone())
    conn.close()
    return item


def create_item(
    business_id: int,
    title: str,
    item_type: str,
    source_reference: str = "",
    plain_text: str = "",
    original_file_path: str = "",
) -> int:
    """Create a new research item. Returns the new item ID."""
    if item_type not in ITEM_TYPES:
        raise ValueError(f"Invalid item type: {item_type}")

    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO research_items 
           (business_id, title, item_type, source_reference, plain_text, original_file_path)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            business_id,
            title,
            item_type,
            source_reference,
            plain_text,
            original_file_path,
        ),
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id


def update_item(
    item_id: int, title: str, source_reference: str, plain_text: str
) -> bool:
    """Update a research item. Returns True if successful."""
    conn = get_db()
    cursor = conn.execute(
        """UPDATE research_items 
           SET title = ?, source_reference = ?, plain_text = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ?""",
        (title, source_reference, plain_text, item_id),
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete_item(item_id: int) -> bool:
    """Delete a research item. Returns True if successful."""
    conn = get_db()
    cursor = conn.execute("DELETE FROM research_items WHERE id = ?", (item_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


# --- Quotes ---


def get_quotes_for_item(item_id: int) -> list[dict]:
    """Get all quotes for a research item."""
    conn = get_db()
    cursor = conn.execute(
        "SELECT * FROM quotes WHERE research_item_id = ? ORDER BY start_offset",
        (item_id,),
    )
    quotes = [dict_from_row(row) for row in cursor.fetchall()]
    conn.close()
    return quotes


def create_quote(item_id: int, start_offset: int, end_offset: int, text: str) -> int:
    """Create a new quote. Returns the new quote ID."""
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO quotes (research_item_id, start_offset, end_offset, text)
           VALUES (?, ?, ?, ?)""",
        (item_id, start_offset, end_offset, text),
    )
    conn.commit()
    quote_id = cursor.lastrowid
    conn.close()
    return quote_id


def delete_quote(quote_id: int) -> bool:
    """Delete a quote. Returns True if successful."""
    conn = get_db()
    cursor = conn.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success
