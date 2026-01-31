"""VRIO Analysis template.

Analyzes resources and capabilities:
- Value: Does the resource provide value?
- Rarity: Is the resource rare?
- Imitability: Is it costly to imitate?
- Organization: Is the firm organized to capture value?
"""

from analyses import AnalysisTemplate, register


@register
class VRIOAnalysis(AnalysisTemplate):
    name = "VRIO Analysis"
    slug = "vrio"
    description = "Analyze resources and capabilities for competitive advantage"

    def get_empty_data(self) -> dict:
        return {"resources": []}

    def get_html_form(self, data: dict) -> str:
        resources = data.get("resources", [])

        rows_html = ""
        for i, resource in enumerate(resources):
            rows_html += f'''
            <tr data-index="{i}">
                <td><input type="text" name="resource_{i}_name" value="{self._escape(resource.get("name", ""))}" placeholder="Resource name"></td>
                <td><input type="checkbox" name="resource_{i}_valuable" {"checked" if resource.get("valuable") else ""}></td>
                <td><input type="checkbox" name="resource_{i}_rare" {"checked" if resource.get("rare") else ""}></td>
                <td><input type="checkbox" name="resource_{i}_costly_to_imitate" {"checked" if resource.get("costly_to_imitate") else ""}></td>
                <td><input type="checkbox" name="resource_{i}_organized" {"checked" if resource.get("organized") else ""}></td>
                <td class="implication">{self._get_implication(resource)}</td>
                <td><button type="button" class="remove-row" onclick="removeVRIORow(this)">×</button></td>
            </tr>
            '''

        return f"""
        <div class="vrio-analysis">
            <table class="vrio-table">
                <thead>
                    <tr>
                        <th>Resource/Capability</th>
                        <th>V<br><small>Valuable</small></th>
                        <th>R<br><small>Rare</small></th>
                        <th>I<br><small>Costly to Imitate</small></th>
                        <th>O<br><small>Organized</small></th>
                        <th>Competitive Implication</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            <button type="button" class="add-item" onclick="addVRIORow()">+ Add Resource</button>
        </div>
        """

    def to_plain_text(self, data: dict) -> str:
        lines = ["# VRIO Analysis", ""]
        resources = data.get("resources", [])

        if not resources:
            lines.append("No resources analyzed.")
            return "\n".join(lines)

        lines.append("| Resource | V | R | I | O | Implication |")
        lines.append("|----------|---|---|---|---|-------------|")

        for resource in resources:
            name = resource.get("name", "")
            v = "✓" if resource.get("valuable") else "✗"
            r = "✓" if resource.get("rare") else "✗"
            i = "✓" if resource.get("costly_to_imitate") else "✗"
            o = "✓" if resource.get("organized") else "✗"
            impl = self._get_implication(resource)
            lines.append(f"| {name} | {v} | {r} | {i} | {o} | {impl} |")

        lines.append("")
        lines.append("## Implications")
        lines.append(
            "- **Sustained Competitive Advantage**: All four criteria met (V+R+I+O)"
        )
        lines.append(
            "- **Temporary Competitive Advantage**: Valuable + Rare + Costly to Imitate"
        )
        lines.append("- **Competitive Parity**: Only Valuable")
        lines.append("- **Competitive Disadvantage**: Not Valuable")

        return "\n".join(lines)

    @staticmethod
    def _get_implication(resource: dict) -> str:
        """Determine competitive implication based on VRIO criteria."""
        if not resource.get("valuable"):
            return "Competitive Disadvantage"
        if not resource.get("rare"):
            return "Competitive Parity"
        if not resource.get("costly_to_imitate"):
            return "Temporary Advantage"
        if not resource.get("organized"):
            return "Unused Advantage"
        return "Sustained Advantage"

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
