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

    LEVELS = ["low", "medium", "high"]

    def get_empty_data(self) -> dict:
        return {force[0]: {"level": "medium", "factors": []} for force in self.FORCES}

    def get_html_form(self, data: dict) -> str:
        html_parts = ['<div class="five-forces-analysis">']

        for key, label, description in self.FORCES:
            force_data = data.get(key, {"level": "medium", "factors": []})
            level = force_data.get("level", "medium")
            factors = force_data.get("factors", [])

            # Level selector
            level_options = "\n".join(
                f'<option value="{l}" {"selected" if l == level else ""}>{l.capitalize()}</option>'
                for l in self.LEVELS
            )

            # Factor items
            factors_html = "\n".join(
                f'<div class="factor-item" data-index="{i}">'
                f'<input type="text" name="{key}_factors[]" value="{self._escape(f)}" placeholder="Add factor...">'
                f'<button type="button" class="remove-item" onclick="removeItem(this)">×</button>'
                f"</div>"
                for i, f in enumerate(factors)
            )

            html_parts.append(f'''
            <div class="force-group" data-force="{key}">
                <h4>{label}</h4>
                <p class="force-description">{description}</p>
                <div class="level-selector">
                    <label>Level:</label>
                    <select name="{key}_level" onchange="updateForce('{key}', this.value)">
                        {level_options}
                    </select>
                </div>
                <div class="force-factors">
                    {factors_html}
                </div>
                <button type="button" class="add-item" onclick="addForceItem('{key}')">+ Add Factor</button>
            </div>
            ''')

        html_parts.append("</div>")
        return "\n".join(html_parts)

    def to_plain_text(self, data: dict) -> str:
        lines = ["# Porter's Five Forces Analysis", ""]

        for key, label, _ in self.FORCES:
            force_data = data.get(key, {"level": "medium", "factors": []})
            level = force_data.get("level", "medium")
            factors = force_data.get("factors", [])

            lines.append(f"## {label}")
            lines.append(f"**Level:** {level.capitalize()}")
            lines.append("")

            if factors:
                lines.append("**Factors:**")
                for f in factors:
                    lines.append(f"- {f}")
            else:
                lines.append("- (No factors identified)")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
