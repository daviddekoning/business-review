"""Porter's Five Forces Analysis template.

Analyzes competitive forces:
- Threat of new entrants
- Bargaining power of suppliers
- Bargaining power of buyers
- Threat of substitutes
- Industry rivalry
"""

from analyses import AnalysisTemplate, register


@register
class FiveForcesAnalysis(AnalysisTemplate):
    name = "Porter's Five Forces"
    slug = "five_forces"
    description = "Analyze competitive forces in the industry"

    FORCES = [
        (
            "new_entrants",
            "Threat of New Entrants",
            "Barriers to entry, capital requirements, economies of scale",
        ),
        (
            "supplier_power",
            "Supplier Power",
            "Number of suppliers, uniqueness, switching costs",
        ),
        (
            "buyer_power",
            "Buyer Power",
            "Number of buyers, price sensitivity, switching costs",
        ),
        (
            "substitutes",
            "Threat of Substitutes",
            "Alternative products, price-performance trade-off",
        ),
        (
            "rivalry",
            "Industry Rivalry",
            "Number of competitors, industry growth, differentiation",
        ),
    ]

    LEVELS = ["high", "medium", "low"]

    def get_empty_data(self) -> dict:
        return {
            force[0]: {"significance": "medium", "description": "", "impact": ""}
            for force in self.FORCES
        }

    def get_html_form(self, data: dict) -> str:
        html_parts = ['<div class="five-forces-analysis">']

        for key, label, help_text in self.FORCES:
            force_data = data.get(key, {})
            # Handle migration/backward compatibility if old format (list of factors) exists
            # by joining factors into description if present, or just defaulting to empty
            if "factors" in force_data:
                # Old format
                significance = force_data.get("level", "medium")
                description = "\n".join(force_data.get("factors", []))
                impact = ""
            else:
                # New format
                significance = force_data.get("significance", "medium")
                description = force_data.get("description", "")
                impact = force_data.get("impact", "")

            # Radio buttons for significance
            radio_options = ""
            for l in self.LEVELS:
                checked = "checked" if l == significance else ""
                radio_options += (
                    f'<label class="radio-option">'
                    f'<input type="radio" name="{key}_significance" value="{l}" {checked}>'
                    f"{l.capitalize()}"
                    f"</label>"
                )

            html_parts.append(f'''
            <div class="force-group" data-force="{key}">
                <div class="force-header">
                    <h4>{label}</h4>
                    <p class="force-help">{help_text}</p>
                </div>
                
                <div class="force-inputs-container">
                    <div class="force-text-areas">
                        <div class="force-text-area-wrapper">
                            <label>Description of Force</label>
                            <textarea name="{key}_description" placeholder="Describe the force...">{self._escape(description)}</textarea>
                        </div>
                        <div class="force-text-area-wrapper">
                            <label>Impact on Business</label>
                            <textarea name="{key}_impact" placeholder="Describe the impact...">{self._escape(impact)}</textarea>
                        </div>
                    </div>
                    
                    <div class="force-significance">
                        <label class="main-label">Significance</label>
                        <div class="radio-group">
                            {radio_options}
                        </div>
                    </div>
                </div>
            </div>
            ''')

        html_parts.append("</div>")
        return "\n".join(html_parts)

    def to_plain_text(self, data: dict) -> str:
        lines = ["# Porter's Five Forces Analysis", ""]

        # Helper to get significance weight
        weights = {"high": 3, "medium": 2, "low": 1}

        # Collect all forces with their data and weight
        forces_with_data = []
        for key, limits, _ in self.FORCES:
            force_data = data.get(key, {})
            if "factors" in force_data:
                # Old format
                significance = force_data.get("level", "medium")
                description = "\n".join(
                    [f"- {f}" for f in force_data.get("factors", [])]
                )
                impact = ""
            else:
                significance = force_data.get("significance", "medium")
                description = force_data.get("description", "")
                impact = force_data.get("impact", "")

            weight = weights.get(significance.lower(), 0)
            forces_with_data.append(
                {
                    "label": limits,  # limits is actually the label in the tuple unpacking above
                    "significance": significance,
                    "description": description,
                    "impact": impact,
                    "weight": weight,
                }
            )

        # Sort by weight descending
        forces_with_data.sort(key=lambda x: x["weight"], reverse=True)

        for force in forces_with_data:
            lines.append(f"## {force['label']}")
            lines.append(f"**Significance:** {force['significance'].capitalize()}")
            lines.append("")

            if force["description"]:
                lines.append("**Description:**")
                lines.append(force["description"])
                lines.append("")

            if force["impact"]:
                lines.append("**Impact:**")
                lines.append(force["impact"])
                lines.append("")

            if not force["description"] and not force["impact"]:
                lines.append("(No details provided)")
                lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _escape(text: str) -> str:
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
