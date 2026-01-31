"""Summary model - CRUD operations for summaries."""

import markdown
from pathlib import Path
from db import get_db, dict_from_row


def get_summary(business_id: int) -> dict | None:
    """Get the summary for a business."""
    conn = get_db()
    cursor = conn.execute(
        "SELECT * FROM summaries WHERE business_id = ?", (business_id,)
    )
    summary = dict_from_row(cursor.fetchone())
    conn.close()
    return summary


def save_summary(business_id: int, markdown_content: str) -> int:
    """Save or update a summary. Returns the summary ID."""
    conn = get_db()

    # Use upsert
    cursor = conn.execute(
        """INSERT INTO summaries (business_id, markdown_content)
           VALUES (?, ?)
           ON CONFLICT(business_id) 
           DO UPDATE SET markdown_content = ?, updated_at = CURRENT_TIMESTAMP""",
        (business_id, markdown_content, markdown_content),
    )
    conn.commit()

    # Get the ID
    cursor = conn.execute(
        "SELECT id FROM summaries WHERE business_id = ?", (business_id,)
    )
    summary_id = cursor.fetchone()["id"]
    conn.close()
    return summary_id


def markdown_to_html(markdown_content: str) -> str:
    """Convert markdown to HTML."""
    return markdown.markdown(
        markdown_content, extensions=["tables", "fenced_code", "toc"]
    )


def export_to_pdf(business_id: int, output_path: str | Path) -> Path:
    """Export summary to PDF. Returns the output path."""
    from weasyprint import HTML, CSS

    summary = get_summary(business_id)
    if not summary:
        raise ValueError(f"No summary found for business {business_id}")

    html_content = markdown_to_html(summary["markdown_content"])

    # Wrap in basic HTML structure with styling
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                color: #333;
            }}
            h1, h2, h3 {{ color: #1a1a2e; }}
            blockquote {{
                border-left: 4px solid #4361ee;
                margin-left: 0;
                padding-left: 20px;
                color: #555;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    HTML(string=full_html).write_pdf(output_path)
    return output_path
