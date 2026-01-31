"""Wardley Map Analysis template (simplified text-based).

Maps components along:
- Value Chain (vertical): Visibility to user
- Evolution (horizontal): Genesis → Custom → Product → Commodity
"""

from analyses import AnalysisTemplate, register


@register
class WardleyMapAnalysis(AnalysisTemplate):
    name = "Wardley Map"
    slug = "wardley"
    description = "Map components by value chain position and evolution stage"

    EVOLUTION_STAGES = [
        ("genesis", "Genesis", "Novel, uncertain, requires research"),
        ("custom", "Custom Built", "Tailored solutions, emerging practices"),
        ("product", "Product/Rental", "Standardized, feature competition"),
        ("commodity", "Commodity/Utility", "Standardized, price competition"),
    ]

    VISIBILITY_LEVELS = [
        ("visible", "Visible", "Directly visible to the customer"),
        ("aware", "Aware", "Customer aware but not main focus"),
        ("hidden", "Hidden", "Behind the scenes, customer unaware"),
    ]

    def get_empty_data(self) -> dict:
        return {"components": []}

    def get_html_form(self, data: dict) -> str:
        components = data.get("components", [])

        evolution_options = "\n".join(
            f'<option value="{k}">{label}</option>'
            for k, label, _ in self.EVOLUTION_STAGES
        )

        visibility_options = "\n".join(
            f'<option value="{k}">{label}</option>'
            for k, label, _ in self.VISIBILITY_LEVELS
        )

        rows_html = ""
        for i, comp in enumerate(components):
            evo_select = "\n".join(
                f'<option value="{k}" {"selected" if comp.get("evolution") == k else ""}>{label}</option>'
                for k, label, _ in self.EVOLUTION_STAGES
            )
            vis_select = "\n".join(
                f'<option value="{k}" {"selected" if comp.get("visibility") == k else ""}>{label}</option>'
                for k, label, _ in self.VISIBILITY_LEVELS
            )

            rows_html += f'''
            <tr data-index="{i}">
                <td><input type="text" name="component_{i}_name" value="{self._escape(comp.get("name", ""))}" placeholder="Component name"></td>
                <td>
                    <select name="component_{i}_evolution">
                        {evo_select}
                    </select>
                </td>
                <td>
                    <select name="component_{i}_visibility">
                        {vis_select}
                    </select>
                </td>
                <td><input type="text" name="component_{i}_notes" value="{self._escape(comp.get("notes", ""))}" placeholder="Notes"></td>
                <td><button type="button" class="remove-row" onclick="removeWardleyRow(this)">×</button></td>
            </tr>
            '''

        return f"""
        <div class="wardley-analysis">
            <p class="analysis-intro">
                Map your value chain components by their evolution stage and visibility to the customer.
            </p>
            
            <table class="wardley-table">
                <thead>
                    <tr>
                        <th>Component</th>
                        <th>Evolution Stage</th>
                        <th>Visibility</th>
                        <th>Notes</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            <button type="button" class="add-item" onclick="addWardleyRow()">+ Add Component</button>
            
            <div class="evolution-legend">
                <h4>Evolution Stages</h4>
                <ul>
                    {"".join(f"<li><strong>{label}:</strong> {desc}</li>" for _, label, desc in self.EVOLUTION_STAGES)}
                </ul>
            </div>
        </div>
        """

    def to_plain_text(self, data: dict) -> str:
        lines = ["# Wardley Map Analysis", ""]
        components = data.get("components", [])

        if not components:
            lines.append("No components mapped.")
            return "\n".join(lines)

        # Group by visibility
        by_visibility = {k: [] for k, _, _ in self.VISIBILITY_LEVELS}
        for comp in components:
            vis = comp.get("visibility", "hidden")
            by_visibility.setdefault(vis, []).append(comp)

        for vis_key, vis_label, vis_desc in self.VISIBILITY_LEVELS:
            comps = by_visibility.get(vis_key, [])
            if comps:
                lines.append(f"## {vis_label} ({vis_desc})")
                for comp in comps:
                    evo_label = next(
                        (
                            label
                            for k, label, _ in self.EVOLUTION_STAGES
                            if k == comp.get("evolution")
                        ),
                        "Unknown",
                    )
                    lines.append(f"- **{comp.get('name', 'Unnamed')}** [{evo_label}]")
                    if comp.get("notes"):
                        lines.append(f"  - {comp['notes']}")
                lines.append("")

        lines.append("## Evolution Stage Summary")
        for evo_key, evo_label, evo_desc in self.EVOLUTION_STAGES:
            count = sum(1 for c in components if c.get("evolution") == evo_key)
            lines.append(f"- **{evo_label}**: {count} components")

        return "\n".join(lines)

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
