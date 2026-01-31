"""Analysis model - CRUD operations for analyses."""

import json
from db import get_db, dict_from_row


def get_analyses_for_business(business_id: int) -> list[dict]:
    """Get all analyses for a business."""
    conn = get_db()
    cursor = conn.execute(
        "SELECT * FROM analyses WHERE business_id = ? ORDER BY template_type",
        (business_id,),
    )
    analyses = []
    for row in cursor.fetchall():
        analysis = dict_from_row(row)
        analysis["data"] = json.loads(analysis["data_json"])
        analyses.append(analysis)
    conn.close()
    return analyses


def get_analysis(business_id: int, template_type: str) -> dict | None:
    """Get an analysis by business ID and template type."""
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


def save_analysis(business_id: int, template_type: str, data: dict) -> int:
    """Save or update an analysis. Returns the analysis ID."""
    data_json = json.dumps(data)
    conn = get_db()

    # Use upsert (INSERT OR REPLACE)
    cursor = conn.execute(
        """INSERT INTO analyses (business_id, template_type, data_json)
           VALUES (?, ?, ?)
           ON CONFLICT(business_id, template_type) 
           DO UPDATE SET data_json = ?, updated_at = CURRENT_TIMESTAMP""",
        (business_id, template_type, data_json, data_json),
    )
    conn.commit()

    # Get the ID
    cursor = conn.execute(
        "SELECT id FROM analyses WHERE business_id = ? AND template_type = ?",
        (business_id, template_type),
    )
    analysis_id = cursor.fetchone()["id"]
    conn.close()
    return analysis_id


def delete_analysis(analysis_id: int) -> bool:
    """Delete an analysis. Returns True if successful."""
    conn = get_db()
    cursor = conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success
