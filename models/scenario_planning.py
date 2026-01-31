"""Scenario Planning model.

Manages scenario planning data for businesses, storing strategies,
possible futures, and analysis for each intersection.
"""

import json
from db import get_db


def get_empty_data() -> dict:
    """Return the default empty data structure for scenario planning."""
    return {"strategies": [], "futures": [], "cells": {}}


def get_scenario_planning(business_id: int) -> dict:
    """Get scenario planning data for a business.

    Args:
        business_id: The business ID

    Returns:
        Dictionary with strategies, futures, and cells data
    """
    db = get_db()
    row = db.execute(
        "SELECT data_json FROM scenario_planning WHERE business_id = ?", (business_id,)
    ).fetchone()

    if row:
        return json.loads(row["data_json"])
    return get_empty_data()


def save_scenario_planning(business_id: int, data: dict) -> None:
    """Save scenario planning data for a business.

    Args:
        business_id: The business ID
        data: Dictionary with strategies, futures, and cells
    """
    db = get_db()
    data_json = json.dumps(data)

    db.execute(
        """INSERT INTO scenario_planning (business_id, data_json, updated_at)
           VALUES (?, ?, CURRENT_TIMESTAMP)
           ON CONFLICT(business_id) DO UPDATE SET
               data_json = excluded.data_json,
               updated_at = CURRENT_TIMESTAMP""",
        (business_id, data_json),
    )
    db.commit()
