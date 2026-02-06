"""PESTEL Analysis template.

PESTEL analyzes macro-environmental factors:
- Political
- Economic
- Social
- Technological
- Environmental
- Legal
"""

from analyses import AnalysisTemplate, register


@register
class PESTELAnalysis(AnalysisTemplate):
    name = "PESTEL Analysis"
    slug = "pestel"
    description = "Analyze macro-environmental factors affecting the business"

    FACTOR_DETAILS = {
        "political": {
            "label": "Political",
            "description": "Government policies, regulations, political stability, trade policies",
        },
        "economic": {
            "label": "Economic",
            "description": "Economic growth, interest rates, inflation, unemployment, exchange rates",
        },
        "social": {
            "label": "Social",
            "description": "Demographics, culture, lifestyle trends, education, health consciousness",
        },
        "technological": {
            "label": "Technological",
            "description": "Innovation, R&D, automation, technology adoption, digital transformation",
        },
        "environmental": {
            "label": "Environmental",
            "description": "Climate change, sustainability, environmental regulations, waste management",
        },
        "legal": {
            "label": "Legal",
            "description": "Employment law, consumer protection, health & safety, antitrust laws",
        },
    }

    DEFAULT_ORDER = [
        "political",
        "economic",
        "social",
        "technological",
        "environmental",
        "legal",
    ]

    def get_empty_data(self) -> dict:
        data = {key: [] for key in self.FACTOR_DETAILS}
        data["order"] = self.DEFAULT_ORDER
        return data

    def get_input_schema(self) -> dict:
        factor_items_schema = {
            "type": "array",
            "description": "List of factors in this category",
            "items": {
                "type": "object",
                "properties": {
                    "factor": {
                        "type": "string",
                        "description": "The environmental factor",
                    },
                    "impact": {
                        "type": "string",
                        "description": "Impact on the business",
                    },
                },
                "required": ["factor"],
            },
        }
        return {
            "type": "object",
            "description": "PESTEL macro-environmental analysis",
            "properties": {
                "political": {
                    **factor_items_schema,
                    "description": "Political factors: government policies, regulations, stability",
                },
                "economic": {
                    **factor_items_schema,
                    "description": "Economic factors: growth, interest rates, inflation",
                },
                "social": {
                    **factor_items_schema,
                    "description": "Social factors: demographics, culture, lifestyle trends",
                },
                "technological": {
                    **factor_items_schema,
                    "description": "Technological factors: innovation, automation, digital",
                },
                "environmental": {
                    **factor_items_schema,
                    "description": "Environmental factors: climate, sustainability, regulations",
                },
                "legal": {
                    **factor_items_schema,
                    "description": "Legal factors: employment law, consumer protection, safety",
                },
                "order": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Order of categories by importance (optional)",
                },
            },
            "required": [
                "political",
                "economic",
                "social",
                "technological",
                "environmental",
                "legal",
            ],
        }

    def get_html_form(self, data: dict) -> str:
        html_parts = ['<div class="pestel-analysis" id="pestel-container">']

        # Get order from data or use default
        order = data.get("order", self.DEFAULT_ORDER)

        # Ensure all factors are present in order (handle missing or extra)
        # Filter order to only include valid keys
        valid_order = [key for key in order if key in self.FACTOR_DETAILS]
        # Add any missing keys to the end
        missing_keys = [key for key in self.FACTOR_DETAILS if key not in valid_order]
        valid_order.extend(missing_keys)

        for key in valid_order:
            details = self.FACTOR_DETAILS[key]
            items = data.get(key, [])

            # Build items HTML
            items_html_parts = []
            for i, item in enumerate(items):
                # Handle backward compatibility: item might be a string
                if isinstance(item, str):
                    factor_text = item
                    impact_text = ""
                else:
                    factor_text = item.get("factor", "")
                    impact_text = item.get("impact", "")

                items_html_parts.append(
                    f'<div class="factor-item" data-index="{i}">'
                    f'<div class="factor-inputs">'
                    f'<input type="text" name="{key}_factor[]" value="{self._escape(factor_text)}" placeholder="Factor" class="factor-input">'
                    f'<input type="text" name="{key}_impact[]" value="{self._escape(impact_text)}" placeholder="Impact on Business" class="impact-input">'
                    f"</div>"
                    f'<button type="button" class="remove-item" onclick="removeItem(this)">×</button>'
                    f"</div>"
                )

            items_html = "\n".join(items_html_parts)

            html_parts.append(f'''
            <div class="factor-group" data-factor="{key}">
                <div class="factor-header">
                    <span class="drag-handle">☰</span>
                    <div class="header-text">
                        <h4>{details["label"]}</h4>
                        <p class="factor-description">{details["description"]}</p>
                    </div>
                </div>
                <div class="factor-items">
                    {items_html}
                </div>
                <button type="button" class="add-item" onclick="addItem('{key}')">+ Add Item</button>
            </div>
            ''')

        html_parts.append("</div>")
        return "\n".join(html_parts)

    def to_plain_text(self, data: dict) -> str:
        lines = [
            "# PESTEL Analysis",
            "(Factors are listed in decreasing order of importance)",
            "",
        ]

        order = data.get("order", self.DEFAULT_ORDER)
        valid_order = [key for key in order if key in self.FACTOR_DETAILS]
        missing_keys = [key for key in self.FACTOR_DETAILS if key not in valid_order]
        valid_order.extend(missing_keys)

        for key in valid_order:
            details = self.FACTOR_DETAILS[key]
            items = data.get(key, [])

            lines.append(f"## {details['label']}")
            if items:
                for item in items:
                    if isinstance(item, str):
                        lines.append(f"- {item}")
                    else:
                        factor = item.get("factor", "")
                        impact = item.get("impact", "")
                        lines.append(f"- Factor: {factor}")
                        if impact:
                            lines.append(f"  Impact: {impact}")
            else:
                lines.append("- (No factors identified)")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _escape(text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
