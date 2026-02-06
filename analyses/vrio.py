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

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "description": "VRIO analysis data structure",
            "properties": {
                "resources": {
                    "type": "array",
                    "description": "Resources/capabilities to analyze for competitive advantage",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the resource or capability",
                            },
                            "description": {
                                "type": "string",
                                "description": "Notes about the resource",
                            },
                            "valuable": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                                "description": "Does this provide value? (1=low, 5=high)",
                            },
                            "rare": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                                "description": "Is this resource rare? (1=common, 5=very rare)",
                            },
                            "costly_to_imitate": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                                "description": "Is it costly to imitate? (1=easy, 5=very difficult)",
                            },
                            "organized": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                                "description": "Is the firm organized to capture value? (1=no, 5=fully)",
                            },
                        },
                        "required": ["name"],
                    },
                }
            },
            "required": ["resources"],
        }

    def get_html_form(self, data: dict) -> str:
        resources = data.get("resources", [])

        rows_html = ""
        for i, resource in enumerate(resources):
            rows_html += f'''
            <tr data-index="{i}" class="vrio-main-row">
                <td>
                    <input type="text" name="resource_{i}_name" value="{self._escape(resource.get("name", ""))}" placeholder="Resource name" class="resource-name">
                </td>
                <td>
                    <div class="slider-container">
                        <input type="range" name="resource_{i}_valuable" min="1" max="5" step="1" value="{resource.get("valuable", 3)}" oninput="this.nextElementSibling.value = this.value">
                        <output>{resource.get("valuable", 3)}</output>
                    </div>
                </td>
                <td>
                    <div class="slider-container">
                        <input type="range" name="resource_{i}_rare" min="1" max="5" step="1" value="{resource.get("rare", 3)}" oninput="this.nextElementSibling.value = this.value">
                        <output>{resource.get("rare", 3)}</output>
                    </div>
                </td>
                <td>
                    <div class="slider-container">
                        <input type="range" name="resource_{i}_costly_to_imitate" min="1" max="5" step="1" value="{resource.get("costly_to_imitate", 3)}" oninput="this.nextElementSibling.value = this.value">
                        <output>{resource.get("costly_to_imitate", 3)}</output>
                    </div>
                </td>
                <td>
                    <div class="slider-container">
                        <input type="range" name="resource_{i}_organized" min="1" max="5" step="1" value="{resource.get("organized", 3)}" oninput="this.nextElementSibling.value = this.value">
                        <output>{resource.get("organized", 3)}</output>
                    </div>
                </td>
                <td class="score-cell">
                    <div class="score-value">-</div>
                    <div class="score-implication"></div>
                </td>
                <td><button type="button" class="remove-row" onclick="removeVRIORow(this)">×</button></td>
            </tr>
            <tr data-index="{i}" class="vrio-desc-row">
                <td colspan="7">
                    <textarea name="resource_{i}_description" placeholder="Description / Notes" rows="2" class="resource-desc">{self._escape(resource.get("description", ""))}</textarea>
                </td>
            </tr>
            '''

        return f"""
        <div class="vrio-analysis">
            <table class="vrio-table">
                <thead>
                    <tr>
                        <th style="width: 25%">Resource</th>
                        <th>V<br><small>Valuable</small></th>
                        <th>R<br><small>Rare</small></th>
                        <th>I<br><small>Inimitable</small></th>
                        <th>O<br><small>Organized</small></th>
                        <th style="width: 15%">Score / Implication</th>
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

        lines.append("| Resource | Description | V | R | I | O | Score | Implication |")
        lines.append("|----------|-------------|---|---|---|---|-------|-------------|")

        # Calculate scores and sort resources
        scored_resources = []
        for resource in resources:
            v = resource.get("valuable", 3)
            r = resource.get("rare", 3)
            i = resource.get("costly_to_imitate", 3)
            o = resource.get("organized", 3)
            score, implication = self._get_score_and_implication(v, r, i, o)
            scored_resources.append(
                {
                    "resource": resource,
                    "score": score,
                    "implication": implication,
                    "v": v,
                    "r": r,
                    "i": i,
                    "o": o,
                }
            )

        # Sort by score descending
        scored_resources.sort(key=lambda x: x["score"], reverse=True)

        for item in scored_resources:
            resource = item["resource"]
            name = resource.get("name", "")
            desc = resource.get("description", "").replace("\n", " ")
            lines.append(
                f"| {name} | {desc} | {item['v']} | {item['r']} | {item['i']} | {item['o']} | {item['score']} | {item['implication']} |"
            )

        lines.append("")
        lines.append("## Scoring Legend (1-5)")
        lines.append("Formula: (V * 0.35) + (R * 0.35) + (I * 0.20) + (O * 0.10)")
        lines.append("- **Sustained Competitive Advantage**: Score >= 4.5")
        lines.append("- **Temporary Competitive Advantage**: 3.5 <= Score < 4.5")
        lines.append("- **Competitive Parity**: 2.5 <= Score < 3.5")
        lines.append("- **Competitive Disadvantage**: Score < 2.5")

        return "\n".join(lines)

    @staticmethod
    def _get_score_and_implication(v, r, i, o) -> tuple[float, str]:
        """Calculate score and determine implication."""
        try:
            v = int(v)
            r = int(r)
            i = int(i)
            o = int(o)
        except (ValueError, TypeError):
            return 0.0, "Invalid Data"

        score = (v * 0.35) + (r * 0.35) + (i * 0.20) + (o * 0.10)
        score = round(score, 1)

        if score >= 4.5:
            return score, "Sustained Advantage"
        elif score >= 3.5:
            return score, "Temporary Advantage"
        elif score >= 2.5:
            return score, "Competitive Parity"
        else:
            return score, "Competitive Disadvantage"

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
