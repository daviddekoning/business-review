"""Business Analysis Webapp - Flask Application."""

import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file

from db import init_db
from db.migrations import run_migrations
from models import business, research, analysis, summary, scenario_planning
import analyses

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["UPLOAD_FOLDER"] = Path(__file__).parent / "uploads"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max upload


# --- Initialization ---


@app.before_request
def ensure_db():
    """Ensure database is initialized and migrated on first request."""
    if not hasattr(app, "_db_initialized"):
        init_db()
        run_migrations()
        app._db_initialized = True


# --- Main Page (Business List) ---


@app.route("/")
def index():
    """Main page - list all businesses."""
    businesses = business.get_all()
    return render_template(
        "index.html", businesses=businesses, business_types=business.BUSINESS_TYPES
    )


@app.route("/business", methods=["POST"])
def create_business():
    """Create a new business."""
    business_id = business.create(
        name=request.form["name"],
        description=request.form.get("description", ""),
        business_type=request.form["type"],
        strategic_question=request.form.get("strategic_question", ""),
    )
    return redirect(url_for("view_business", business_id=business_id))


@app.route("/business/<int:business_id>")
def view_business(business_id: int):
    """View a business with tabs for research, analysis, summary."""
    biz = business.get_by_id(business_id)
    if not biz:
        return "Business not found", 404

    # Get all data for this business
    research_items = research.get_items_for_business(business_id)

    # Get quotes for each research item
    for item in research_items:
        item["quotes"] = research.get_quotes_for_item(item["id"])

    # Get analyses (list of created analyses)
    biz_analyses = analysis.get_analyses_for_business(business_id)
    # Attach template info to each analysis
    for a in biz_analyses:
        a["template"] = analyses.get_template(a["template_type"])

    # Get summary
    biz_summary = summary.get_summary(business_id)

    # Get scenario planning
    scenario_data = scenario_planning.get_scenario_planning(business_id)

    return render_template(
        "business.html",
        business=biz,
        business_types=business.BUSINESS_TYPES,
        research_items=research_items,
        research_types=research.ITEM_TYPES,
        analyses=biz_analyses,
        analysis_templates=analyses.get_all_templates(),
        summary=biz_summary,
        scenario_planning=scenario_data,
    )


@app.route("/business/<int:business_id>/update", methods=["POST"])
def update_business(business_id: int):
    """Update a business."""
    business.update(
        business_id=business_id,
        name=request.form["name"],
        description=request.form.get("description", ""),
        business_type=request.form["type"],
        strategic_question=request.form.get("strategic_question", ""),
    )
    return redirect(url_for("view_business", business_id=business_id))


@app.route("/business/<int:business_id>/delete", methods=["POST"])
def delete_business(business_id: int):
    """Delete a business."""
    business.delete(business_id)
    return redirect(url_for("index"))


# --- Research Items ---


@app.route("/business/<int:business_id>/research", methods=["POST"])
def create_research_item(business_id: int):
    """Create a new research item."""
    title = request.form["title"]
    item_type = request.form["type"]
    source_reference = request.form.get("source_reference", "")
    plain_text = request.form.get("plain_text", "")
    original_file_path = ""

    # Handle file upload
    if "file" in request.files:
        file = request.files["file"]
        if file.filename:
            upload_dir = research.ensure_upload_dir(business_id)
            file_path = upload_dir / file.filename
            file.save(file_path)
            original_file_path = str(file_path)

            # Try to extract text if it's a PDF or audio
            if not plain_text:
                try:
                    from services import gemini

                    ext = file_path.suffix.lower()
                    if ext == ".pdf":
                        plain_text = gemini.extract_text_from_pdf(file_path)
                    elif ext in [".mp3", ".wav", ".m4a", ".ogg", ".flac"]:
                        plain_text = gemini.transcribe_audio(file_path)
                except Exception as e:
                    # Log error but continue - user can paste text manually
                    print(f"Error extracting text: {e}")

    # Try to extract text from URL if provided and no text yet
    if (
        not plain_text
        and source_reference
        and source_reference.startswith(("http://", "https://"))
    ):
        try:
            from services import extractor

            text = extractor.extract_from_url(source_reference)
            if text:
                plain_text = text
        except Exception as e:
            print(f"Error extracting from URL: {e}")

    research.create_item(
        business_id=business_id,
        title=title,
        item_type=item_type,
        source_reference=source_reference,
        plain_text=plain_text,
        original_file_path=original_file_path,
    )
    return redirect(url_for("view_business", business_id=business_id) + "#research")


@app.route("/research/<int:item_id>/update", methods=["POST"])
def update_research_item(item_id: int):
    """Update a research item."""
    item = research.get_item_by_id(item_id)
    if not item:
        return "Item not found", 404

    research.update_item(
        item_id=item_id,
        title=request.form["title"],
        source_reference=request.form.get("source_reference", ""),
        plain_text=request.form.get("plain_text", ""),
    )
    return redirect(
        url_for("view_business", business_id=item["business_id"]) + "#research"
    )


@app.route("/research/<int:item_id>/delete", methods=["POST"])
def delete_research_item(item_id: int):
    """Delete a research item."""
    item = research.get_item_by_id(item_id)
    if not item:
        return "Item not found", 404

    business_id = item["business_id"]
    research.delete_item(item_id)
    return redirect(url_for("view_business", business_id=business_id) + "#research")


# --- Quotes ---


@app.route("/research/<int:item_id>/quote", methods=["POST"])
def create_quote(item_id: int):
    """Create a new quote from selection."""
    data = request.get_json()
    quote_id = research.create_quote(
        item_id=item_id,
        start_offset=data["start_offset"],
        end_offset=data["end_offset"],
        text=data["text"],
    )
    return jsonify({"id": quote_id, "success": True})


@app.route("/quote/<int:quote_id>/delete", methods=["POST"])
def delete_quote(quote_id: int):
    """Delete a quote."""
    research.delete_quote(quote_id)
    return jsonify({"success": True})


# --- Analyses ---


@app.route("/business/<int:business_id>/analysis", methods=["POST"])
def create_analysis_route(business_id: int):
    """Create a new analysis."""
    data = request.get_json()
    template_type = data.get("template_type")
    name = data.get("name", "")

    template = analyses.get_template(template_type)
    if not template:
        return jsonify({"error": "Unknown analysis type"}), 404

    if not name:
        name = template.name

    analysis_id = analysis.create_analysis(business_id, template_type, name)
    return jsonify({"success": True, "id": analysis_id, "name": name})


@app.route("/business/<int:business_id>/analysis/<int:analysis_id>", methods=["PUT"])
def save_analysis_route(business_id: int, analysis_id: int):
    """Save analysis data."""
    existing = analysis.get_analysis_by_id(analysis_id)
    if not existing or existing["business_id"] != business_id:
        return jsonify({"error": "Analysis not found"}), 404

    data = request.get_json()
    analysis.save_analysis_by_id(analysis_id, data)
    return jsonify({"success": True})


@app.route(
    "/business/<int:business_id>/analysis/<int:analysis_id>/name", methods=["PUT"]
)
def update_analysis_name_route(business_id: int, analysis_id: int):
    """Update analysis name."""
    existing = analysis.get_analysis_by_id(analysis_id)
    if not existing or existing["business_id"] != business_id:
        return jsonify({"error": "Analysis not found"}), 404

    data = request.get_json()
    name = data.get("name", "")
    if not name:
        return jsonify({"error": "Name is required"}), 400

    analysis.update_analysis_name(analysis_id, name)
    return jsonify({"success": True})


@app.route("/business/<int:business_id>/analysis/<int:analysis_id>", methods=["DELETE"])
def delete_analysis_route(business_id: int, analysis_id: int):
    """Delete an analysis."""
    existing = analysis.get_analysis_by_id(analysis_id)
    if not existing or existing["business_id"] != business_id:
        return jsonify({"error": "Analysis not found"}), 404

    analysis.delete_analysis(analysis_id)
    return jsonify({"success": True})


# Keep old route for backward compatibility
@app.route("/business/<int:business_id>/analysis/<slug>", methods=["POST"])
def save_analysis_legacy(business_id: int, slug: str):
    """Save analysis data (legacy route)."""
    template = analyses.get_template(slug)
    if not template:
        return "Unknown analysis type", 404

    data = request.get_json()
    analysis.save_analysis(business_id, slug, data)
    return jsonify({"success": True})


@app.route("/business/<int:business_id>/analysis/<slug>/text")
def get_analysis_text(business_id: int, slug: str):
    """Get analysis as plain text (for LLM consumption)."""
    template = analyses.get_template(slug)
    if not template:
        return "Unknown analysis type", 404

    existing = analysis.get_analysis(business_id, slug)
    data = existing["data"] if existing else template.get_empty_data()
    return template.to_plain_text(data), 200, {"Content-Type": "text/plain"}


# --- Scenario Planning ---


@app.route("/business/<int:business_id>/scenario-planning", methods=["POST"])
def save_scenario_planning_route(business_id: int):
    """Save scenario planning data."""
    data = request.get_json()
    scenario_planning.save_scenario_planning(business_id, data)
    return jsonify({"success": True})


# --- Summary ---


@app.route("/business/<int:business_id>/summary", methods=["POST"])
def save_summary(business_id: int):
    """Save summary markdown."""
    data = request.get_json()
    summary.save_summary(business_id, data["markdown"])
    return jsonify({"success": True})


@app.route("/business/<int:business_id>/summary/pdf")
def export_summary_pdf(business_id: int):
    """Export summary as PDF."""
    biz = business.get_by_id(business_id)
    if not biz:
        return "Business not found", 404

    output_path = Path(app.config["UPLOAD_FOLDER"]) / str(business_id) / "summary.pdf"
    try:
        summary.export_to_pdf(business_id, output_path)
        return send_file(
            output_path, as_attachment=True, download_name=f"{biz['name']}_summary.pdf"
        )
    except ValueError as e:
        return str(e), 400


if __name__ == "__main__":
    app.run(debug=True, port=5001)
