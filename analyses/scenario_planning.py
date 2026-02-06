"""Scenario Planning Analysis template.

Scenario planning creates a matrix of strategies vs. possible futures,
allowing analysis of how each strategy performs under different scenarios.
"""

from analyses import AnalysisTemplate, register


@register
class ScenarioPlanningAnalysis(AnalysisTemplate):
    name = "Scenario Planning"
    slug = "scenario_planning"
    description = "Analyze strategies against possible futures in a matrix format"

    def get_empty_data(self) -> dict:
        """Return the default empty data structure for scenario planning."""
        return {"strategies": [], "futures": [], "cells": {}}

    def get_html_form(self, data: dict) -> str:
        """Return HTML form for scenario planning grid."""
        strategies = data.get("strategies", [])
        futures = data.get("futures", [])
        cells = data.get("cells", {})

        # Build the scenario planning HTML
        html_parts = ['<div class="scenario-planning-analysis">']

        # Action buttons
        html_parts.append("""
            <div class="scenario-actions" style="margin-bottom: 1rem;">
                <button type="button" class="btn btn-secondary" onclick="addStrategy(this)">+ Add Strategy</button>
                <button type="button" class="btn btn-secondary" onclick="addFuture(this)">+ Add Future</button>
            </div>
        """)

        if strategies or futures:
            html_parts.append('<div class="scenario-grid-container">')
            html_parts.append('<table class="scenario-grid">')

            # Header row with strategies
            html_parts.append("<thead><tr>")
            html_parts.append('<th class="corner-cell">Futures \\ Strategies</th>')
            for strategy in strategies:
                sid = self._escape(strategy.get("id", ""))
                sname = self._escape(strategy.get("name", ""))
                html_parts.append(f'''
                    <th class="strategy-header" data-id="{sid}">
                        <div class="header-content">
                            <input type="text" class="strategy-name" value="{sname}" placeholder="Strategy name">
                            <button type="button" class="remove-btn" onclick="removeStrategyFromForm(this, '{sid}')">×</button>
                        </div>
                    </th>
                ''')
            html_parts.append("</tr></thead>")

            # Body rows with futures
            html_parts.append("<tbody>")
            for future in futures:
                fid = self._escape(future.get("id", ""))
                fname = self._escape(future.get("name", ""))
                html_parts.append(f'<tr data-future-id="{fid}">')
                html_parts.append(f'''
                    <td class="future-header">
                        <div class="header-content">
                            <input type="text" class="future-name" value="{fname}" placeholder="Future name">
                            <button type="button" class="remove-btn" onclick="removeFutureFromForm(this, '{fid}')">×</button>
                        </div>
                    </td>
                ''')
                for strategy in strategies:
                    sid = strategy.get("id", "")
                    cell_key = f"{sid}_{fid}"
                    cell = cells.get(cell_key, {})
                    summary = self._escape(cell.get("summary", ""))
                    rag = cell.get("rag", "")  # red, amber, green, or empty
                    rag_class = f"rag-{rag}" if rag else ""
                    has_summary = "has-summary" if summary else ""
                    html_parts.append(f'''
                        <td class="scenario-cell {has_summary} {rag_class}" 
                            data-strategy-id="{self._escape(sid)}" 
                            data-future-id="{fid}"
                            onclick="selectScenarioCellInForm(this, '{self._escape(sid)}', '{fid}')">
                            <span class="cell-summary">{summary or "—"}</span>
                        </td>
                    ''')
                html_parts.append("</tr>")
            html_parts.append("</tbody>")

            html_parts.append("</table>")
            html_parts.append("</div>")
        else:
            html_parts.append("""
                <div class="empty-state">
                    <p>No strategies or futures defined yet. Add strategies (columns) and possible futures (rows) to start scenario planning.</p>
                </div>
            """)

        # Hidden data storage
        import json

        data_json = self._escape(json.dumps(data))
        html_parts.append(
            f'<input type="hidden" class="scenario-data" value="{data_json}">'
        )

        # Detail Panel
        html_parts.append("""
            <div class="scenario-detail-panel" style="display: none;">
                <div class="detail-header">
                    <h3>Scenario Analysis</h3>
                    <button type="button" class="close-btn" onclick="closeScenarioDetailInForm(this)">×</button>
                </div>
                <div class="detail-content">
                    <div class="detail-descriptions">
                        <div class="description-box">
                            <label class="strategy-description-label">Strategy Description</label>
                            <textarea class="strategy-description" placeholder="Describe this strategy..."></textarea>
                        </div>
                        <div class="description-box">
                            <label class="future-description-label">Future Description</label>
                            <textarea class="future-description" placeholder="Describe this possible future..."></textarea>
                        </div>
                    </div>
                    <div class="detail-rag">
                        <label>Rating</label>
                        <div class="rag-selector">
                            <button type="button" class="rag-btn rag-btn-green" data-rag="green" onclick="setScenarioRag(this, 'green')" title="Green - Good">●</button>
                            <button type="button" class="rag-btn rag-btn-amber" data-rag="amber" onclick="setScenarioRag(this, 'amber')" title="Amber - Caution">●</button>
                            <button type="button" class="rag-btn rag-btn-red" data-rag="red" onclick="setScenarioRag(this, 'red')" title="Red - Risk">●</button>
                            <button type="button" class="rag-btn rag-btn-none" data-rag="" onclick="setScenarioRag(this, '')" title="Clear">○</button>
                        </div>
                    </div>
                    <div class="detail-analysis">
                        <label>Your Analysis</label>
                        <textarea class="cell-thoughts" placeholder="How does this strategy perform in this future? What are the implications?"></textarea>
                    </div>
                    <div class="detail-summary">
                        <label>Summary (shown in grid)</label>
                        <input type="text" class="cell-summary-input" placeholder="Brief summary for the grid cell">
                    </div>
                </div>
            </div>
        """)

        html_parts.append("</div>")
        return "\n".join(html_parts)

    def to_plain_text(self, data: dict) -> str:
        """Convert scenario planning data to plain text."""
        lines = ["# Scenario Planning", ""]

        strategies = data.get("strategies", [])
        futures = data.get("futures", [])
        cells = data.get("cells", {})

        if not strategies and not futures:
            lines.append("No strategies or futures defined.")
            return "\n".join(lines)

        # List strategies
        lines.append("## Strategies")
        for s in strategies:
            name = s.get("name", "Unnamed")
            desc = s.get("description", "")
            lines.append(f"### {name}")
            if desc:
                lines.append(desc)
            lines.append("")

        # List futures
        lines.append("## Possible Futures")
        for f in futures:
            name = f.get("name", "Unnamed")
            desc = f.get("description", "")
            lines.append(f"### {name}")
            if desc:
                lines.append(desc)
            lines.append("")

        # Matrix analysis
        lines.append("## Scenario Analysis Matrix")
        for f in futures:
            fname = f.get("name", "Unnamed Future")
            fid = f.get("id", "")
            lines.append(f"### Future: {fname}")
            for s in strategies:
                sname = s.get("name", "Unnamed Strategy")
                sid = s.get("id", "")
                cell_key = f"{sid}_{fid}"
                cell = cells.get(cell_key, {})
                summary = cell.get("summary", "")
                thoughts = cell.get("thoughts", "")
                rag = cell.get("rag", "")
                rag_label = {
                    "green": "🟢 Green",
                    "amber": "🟡 Amber",
                    "red": "🔴 Red",
                }.get(rag, "")
                lines.append(f"#### Strategy: {sname}")
                if rag_label:
                    lines.append(f"**Rating**: {rag_label}")
                if summary:
                    lines.append(f"**Summary**: {summary}")
                if thoughts:
                    lines.append(f"**Analysis**: {thoughts}")
                if not summary and not thoughts and not rag:
                    lines.append("(No analysis yet)")
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
