"""Tests for analysis template schemas."""

import pytest
from analyses import get_all_templates, AnalysisTemplate


class TestAnalysisSchemas:
    """Test that all analysis templates have valid input schemas."""

    @pytest.fixture
    def all_templates(self) -> list[AnalysisTemplate]:
        """Get all registered analysis templates."""
        return get_all_templates()

    def test_all_templates_have_input_schema(self, all_templates):
        """Every template must implement get_input_schema()."""
        for template in all_templates:
            schema = template.get_input_schema()
            assert isinstance(schema, dict), (
                f"{template.slug} get_input_schema() must return a dict"
            )
            assert "type" in schema, f"{template.slug} schema must have a 'type' field"
            assert schema["type"] == "object", (
                f"{template.slug} schema type must be 'object'"
            )

    def test_schemas_have_properties(self, all_templates):
        """All schemas must define properties."""
        for template in all_templates:
            schema = template.get_input_schema()
            assert "properties" in schema, (
                f"{template.slug} schema must have 'properties'"
            )
            assert isinstance(schema["properties"], dict), (
                f"{template.slug} properties must be a dict"
            )
            assert len(schema["properties"]) > 0, (
                f"{template.slug} must have at least one property"
            )

    def test_schemas_have_descriptions(self, all_templates):
        """All schemas must have a top-level description."""
        for template in all_templates:
            schema = template.get_input_schema()
            assert "description" in schema, (
                f"{template.slug} schema must have a description"
            )
            assert len(schema["description"]) > 0, (
                f"{template.slug} description must not be empty"
            )

    def test_empty_data_matches_schema_structure(self, all_templates):
        """get_empty_data() should return data that matches the schema structure."""
        for template in all_templates:
            schema = template.get_input_schema()
            empty_data = template.get_empty_data()

            # Check that required fields from schema exist in empty_data
            required_fields = schema.get("required", [])
            for field in required_fields:
                assert field in empty_data, (
                    f"{template.slug} get_empty_data() missing required field '{field}'"
                )

    def test_schema_property_types_are_valid(self, all_templates):
        """Schema properties must have valid JSON Schema types."""
        valid_types = {
            "string",
            "integer",
            "number",
            "boolean",
            "array",
            "object",
            "null",
        }

        def check_properties(props: dict, path: str):
            for name, prop in props.items():
                if "type" in prop:
                    assert prop["type"] in valid_types, (
                        f"Invalid type '{prop['type']}' at {path}.{name}"
                    )
                # Recursively check nested objects
                if prop.get("type") == "object" and "properties" in prop:
                    check_properties(prop["properties"], f"{path}.{name}")
                # Check array items
                if prop.get("type") == "array" and "items" in prop:
                    items = prop["items"]
                    if isinstance(items, dict) and items.get("type") == "object":
                        if "properties" in items:
                            check_properties(items["properties"], f"{path}.{name}[]")

        for template in all_templates:
            schema = template.get_input_schema()
            check_properties(schema.get("properties", {}), template.slug)


class TestSpecificSchemas:
    """Test specific schema requirements for each analysis type."""

    def test_vrio_schema_has_resources(self):
        """VRIO schema must have resources array with VRIO fields."""
        from analyses.vrio import VRIOAnalysis

        template = VRIOAnalysis()
        schema = template.get_input_schema()

        assert "resources" in schema["properties"]
        resources = schema["properties"]["resources"]
        assert resources["type"] == "array"

        # Check resource item has VRIO fields
        item_props = resources["items"]["properties"]
        assert "valuable" in item_props
        assert "rare" in item_props
        assert "costly_to_imitate" in item_props
        assert "organized" in item_props

    def test_five_forces_schema_has_all_forces(self):
        """Five Forces schema must have all 5 forces."""
        from analyses.five_forces import FiveForcesAnalysis

        template = FiveForcesAnalysis()
        schema = template.get_input_schema()

        expected_forces = [
            "new_entrants",
            "supplier_power",
            "buyer_power",
            "substitutes",
            "rivalry",
        ]
        for force in expected_forces:
            assert force in schema["properties"], f"Missing force: {force}"

    def test_pestel_schema_has_all_factors(self):
        """PESTEL schema must have all 6 factors."""
        from analyses.pestel import PESTELAnalysis

        template = PESTELAnalysis()
        schema = template.get_input_schema()

        expected_factors = [
            "political",
            "economic",
            "social",
            "technological",
            "environmental",
            "legal",
        ]
        for factor in expected_factors:
            assert factor in schema["properties"], f"Missing factor: {factor}"

    def test_wardley_schema_has_components(self):
        """Wardley schema must have components with evolution and visibility."""
        from analyses.wardley import WardleyMapAnalysis

        template = WardleyMapAnalysis()
        schema = template.get_input_schema()

        assert "components" in schema["properties"]
        items = schema["properties"]["components"]["items"]
        assert "evolution" in items["properties"]
        assert "visibility" in items["properties"]

    def test_scenario_planning_schema_has_matrix_structure(self):
        """Scenario Planning schema must have strategies, futures, and cells."""
        from analyses.scenario_planning import ScenarioPlanningAnalysis

        template = ScenarioPlanningAnalysis()
        schema = template.get_input_schema()

        assert "strategies" in schema["properties"]
        assert "futures" in schema["properties"]
        assert "cells" in schema["properties"]
