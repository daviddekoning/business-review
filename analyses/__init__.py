"""Analysis templates plugin system.

To add a new analysis template:
1. Create a new file in this directory (e.g., swot.py)
2. Create a class that inherits from AnalysisTemplate
3. Import it in this file to register it

Example:
    class SWOTAnalysis(AnalysisTemplate):
        name = "SWOT Analysis"
        slug = "swot"

        def get_empty_data(self):
            return {"strengths": [], "weaknesses": [], ...}

        def get_html_form(self, data):
            return "<div>...</div>"

        def to_plain_text(self, data):
            return "Strengths: ..."
"""

from abc import ABC, abstractmethod


class AnalysisTemplate(ABC):
    """Base class for analysis templates."""

    name: str = ""  # Display name (e.g., "PESTEL Analysis")
    slug: str = ""  # URL-safe identifier (e.g., "pestel")
    description: str = ""  # Brief description

    @abstractmethod
    def get_empty_data(self) -> dict:
        """Return the default empty data structure for this analysis."""
        pass

    @abstractmethod
    def get_html_form(self, data: dict) -> str:
        """Return HTML form fragment for editing this analysis."""
        pass

    @abstractmethod
    def to_plain_text(self, data: dict) -> str:
        """Convert the analysis data to plain text for LLM consumption."""
        pass

    @abstractmethod
    def get_input_schema(self) -> dict:
        """Return JSON Schema describing the analysis data structure.

        This schema defines what data the analysis expects and can be used for:
        - Validating user/AI input
        - Guiding LLMs to generate valid analysis data
        - Documenting the expected structure
        """
        pass


# Registry of all available templates
REGISTRY: dict[str, AnalysisTemplate] = {}


def register(template_class: type[AnalysisTemplate]) -> type[AnalysisTemplate]:
    """Decorator to register a template class."""
    instance = template_class()
    REGISTRY[instance.slug] = instance
    return template_class


def get_template(slug: str) -> AnalysisTemplate | None:
    """Get a template by slug."""
    return REGISTRY.get(slug)


def get_all_templates() -> list[AnalysisTemplate]:
    """Get all registered templates."""
    return list(REGISTRY.values())


# Import templates to register them
from analyses.pestel import PESTELAnalysis
from analyses.five_forces import FiveForcesAnalysis
from analyses.vrio import VRIOAnalysis
from analyses.wardley import WardleyMapAnalysis
from analyses.scenario_planning import ScenarioPlanningAnalysis
