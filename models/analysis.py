"""Analysis model - CRUD operations for analyses."""

import json
from db import get_db, dict_from_row
import analyses as analysis_templates


def get_analyses_for_business(business_id: int) -> list[dict]:
    """Get all analyses for a business."""
    conn = get_db()
    cursor = conn.execute(
        "SELECT * FROM analyses WHERE business_id = ? ORDER BY created_at",
        (business_id,),
    )
    result = []
    for row in cursor.fetchall():
        analysis = dict_from_row(row)
        analysis["data"] = json.loads(analysis["data_json"])
        result.append(analysis)
    conn.close()
    return result


def get_analysis_by_id(analysis_id: int) -> dict | None:
    """Get an analysis by ID."""
    conn = get_db()
    cursor = conn.execute(
        "SELECT * FROM analyses WHERE id = ?",
        (analysis_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        analysis = dict_from_row(row)
        analysis["data"] = json.loads(analysis["data_json"])
        return analysis
    return None


def get_analysis(business_id: int, template_type: str) -> dict | None:
    """Get an analysis by business ID and template type.

    DEPRECATED: Use get_analysis_by_id instead.
    Kept for backward compatibility.
    """
    conn = get_db()
    cursor = conn.execute(
        "SELECT * FROM analyses WHERE business_id = ? AND template_type = ?",
        (business_id, template_type),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        analysis = dict_from_row(row)
        analysis["data"] = json.loads(analysis["data_json"])
        return analysis
    return None


def create_analysis(business_id: int, template_type: str, name: str) -> int:
    """Create a new analysis. Returns the analysis ID."""
    template = analysis_templates.get_template(template_type)
    if not template:
        raise ValueError(f"Unknown analysis template: {template_type}")

    empty_data = template.get_empty_data()
    data_json = json.dumps(empty_data)

    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO analyses (business_id, name, template_type, data_json)
           VALUES (?, ?, ?, ?)""",
        (business_id, name, template_type, data_json),
    )
    conn.commit()
    analysis_id = cursor.lastrowid
    conn.close()
    return analysis_id


def save_analysis_by_id(analysis_id: int, data: dict) -> bool:
    """Save analysis data by ID. Returns True if successful."""
    data_json = json.dumps(data)
    conn = get_db()
    cursor = conn.execute(
        """UPDATE analyses 
           SET data_json = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ?""",
        (data_json, analysis_id),
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def save_analysis(business_id: int, template_type: str, data: dict) -> int:
    """Save or update an analysis. Returns the analysis ID.

    DEPRECATED: Use save_analysis_by_id instead.
    Kept for backward compatibility - will update the first matching analysis.
    """
    data_json = json.dumps(data)
    conn = get_db()

    # Check if an analysis of this type exists
    cursor = conn.execute(
        "SELECT id FROM analyses WHERE business_id = ? AND template_type = ?",
        (business_id, template_type),
    )
    existing = cursor.fetchone()

    if existing:
        # Update existing
        conn.execute(
            """UPDATE analyses 
               SET data_json = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (data_json, existing["id"]),
        )
        analysis_id = existing["id"]
    else:
        # Create new with default name
        template = analysis_templates.get_template(template_type)
        name = template.name if template else template_type
        cursor = conn.execute(
            """INSERT INTO analyses (business_id, name, template_type, data_json)
               VALUES (?, ?, ?, ?)""",
            (business_id, name, template_type, data_json),
        )
        analysis_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return analysis_id


def update_analysis_name(analysis_id: int, name: str) -> bool:
    """Update an analysis name. Returns True if successful."""
    conn = get_db()
    cursor = conn.execute(
        """UPDATE analyses 
           SET name = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ?""",
        (name, analysis_id),
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete_analysis(analysis_id: int) -> bool:
    """Delete an analysis. Returns True if successful."""
    conn = get_db()
    cursor = conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success
