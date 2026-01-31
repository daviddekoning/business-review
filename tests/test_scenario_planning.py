"""Tests for the scenario planning model."""

import json
from unittest.mock import patch, MagicMock
from models import scenario_planning


def test_get_empty_data_structure():
    """Test that get_empty_data returns the correct structure."""
    data = scenario_planning.get_empty_data()

    assert "strategies" in data
    assert "futures" in data
    assert "cells" in data
    assert isinstance(data["strategies"], list)
    assert isinstance(data["futures"], list)
    assert isinstance(data["cells"], dict)
    assert len(data["strategies"]) == 0
    assert len(data["futures"]) == 0
    assert len(data["cells"]) == 0


def test_get_scenario_planning_returns_empty_for_new_business():
    """Test that get_scenario_planning returns empty data for a new business."""
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchone.return_value = None

    with patch("models.scenario_planning.get_db", return_value=mock_db):
        result = scenario_planning.get_scenario_planning(999)

    assert result == scenario_planning.get_empty_data()
    mock_db.execute.assert_called_once()


def test_get_scenario_planning_returns_existing_data():
    """Test that get_scenario_planning returns existing data correctly."""
    test_data = {
        "strategies": [{"id": "s1", "name": "Strategy 1", "description": "Desc 1"}],
        "futures": [{"id": "f1", "name": "Future 1", "description": "Desc 1"}],
        "cells": {"s1_f1": {"thoughts": "Analysis", "summary": "Summary"}},
    }

    mock_db = MagicMock()
    mock_db.execute.return_value.fetchone.return_value = {
        "data_json": json.dumps(test_data)
    }

    with patch("models.scenario_planning.get_db", return_value=mock_db):
        result = scenario_planning.get_scenario_planning(1)

    assert result == test_data
    assert len(result["strategies"]) == 1
    assert result["strategies"][0]["name"] == "Strategy 1"
    assert result["cells"]["s1_f1"]["summary"] == "Summary"


def test_save_scenario_planning_inserts_new_data():
    """Test that save_scenario_planning correctly saves new data."""
    test_data = {
        "strategies": [{"id": "s1", "name": "Test Strategy", "description": ""}],
        "futures": [],
        "cells": {},
    }

    mock_db = MagicMock()

    with patch("models.scenario_planning.get_db", return_value=mock_db):
        scenario_planning.save_scenario_planning(1, test_data)

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()

    # Check that JSON was properly serialized
    call_args = mock_db.execute.call_args
    assert call_args[0][1][0] == 1  # business_id
    assert json.loads(call_args[0][1][1]) == test_data  # data_json


def test_save_scenario_planning_updates_existing_data():
    """Test that save_scenario_planning updates existing data using upsert."""
    test_data = {
        "strategies": [
            {"id": "s1", "name": "Strategy A", "description": "First strategy"},
            {"id": "s2", "name": "Strategy B", "description": "Second strategy"},
        ],
        "futures": [{"id": "f1", "name": "Optimistic", "description": "Best case"}],
        "cells": {
            "s1_f1": {"thoughts": "Works well", "summary": "Good fit"},
            "s2_f1": {"thoughts": "Risky", "summary": "Uncertain"},
        },
    }

    mock_db = MagicMock()

    with patch("models.scenario_planning.get_db", return_value=mock_db):
        scenario_planning.save_scenario_planning(1, test_data)

    # Verify upsert SQL is used
    call_args = mock_db.execute.call_args
    sql = call_args[0][0]
    assert "ON CONFLICT" in sql
    assert "DO UPDATE" in sql
