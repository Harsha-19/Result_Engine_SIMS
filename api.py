from pydoc import doc
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import pandas as pd
from app.main import process_results
from docx import Document  # type: ignore[import]
from docx.shared import Inches  # type: ignore[import]
from docx.oxml import OxmlElement  # type: ignore[import]
from docx.oxml.ns import qn  # type: ignore[import]
from docx.enum.text import WD_ALIGN_PARAGRAPH  # type: ignore[import]
import json

app = Flask(__name__)
CORS (app, resources={r"/*": {"origins": "https://result-engine-sims.vercel.app"}},)

UPLOAD_FOLDER = "uploads"
EXPORT_FOLDER = "outputs"
TEMPLATE_FOLDER = os.path.join("app", "templates")


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return jsonify({"message": "Result Engine API Running"})


# ===================== UPLOAD =====================
@app.route("/upload", methods=["POST"])
def upload():
    marks_file = request.files.get("marks")
    caste_file = request.files.get("caste")
    ui_meta = request.form.get("ui_meta")

    if not marks_file or not caste_file:
        return jsonify({"error": "Both files required"}), 400

    ui_meta = json.loads(ui_meta) if ui_meta else None

    marks_path = os.path.join(UPLOAD_FOLDER, marks_file.filename)
    caste_path = os.path.join(UPLOAD_FOLDER, caste_file.filename)

    marks_file.save(marks_path)
    caste_file.save(caste_path)

    app.config["MARKS_PATH"] = marks_path
    app.config["CASTE_PATH"] = caste_path
    app.config["UI_META"] = ui_meta

    results = process_results(marks_path, caste_path, ui_meta)

    return jsonify(results)


# ===================== GENERATE DOCX =====================
@app.route("/generate-report", methods=["GET", "POST"])
@app.route("/download", methods=["GET", "POST"])
def generate_doc_report():

    if "MARKS_PATH" not in app.config:
        return jsonify({"error": "No processed data available"}), 400

    # Backward compatible: when missing, behave exactly like existing implementation.
    # Supported: ?format=internal (default), ?format=public
    download_format = (request.args.get("format") or "internal").strip().lower()
    if download_format not in {"internal", "public"}:
        download_format = "internal"

    # Prefer UI meta sent with this request (POST), fall back to stored one from upload
    ui_meta = app.config.get("UI_META")

    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        incoming_meta = payload.get("ui_meta")
        print("Incoming ui_meta from UI:", incoming_meta)
        if incoming_meta:
            ui_meta = incoming_meta
            app.config["UI_META"] = ui_meta

    print("Using ui_meta in generate-report:", ui_meta)

    data = process_results(
        app.config["MARKS_PATH"],
        app.config["CASTE_PATH"],
        ui_meta
    )

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(
        BASE_DIR,
        "templates",
        "Approved Result Analysis Tabulation 2025-26.docx"
    )
    output_path = os.path.join(
    EXPORT_FOLDER,
    "Approved_Result_Analysis.docx"
    )

    print("Template path:", template_path)
    print("Exists:",os.path.exists(template_path))
    doc = Document(template_path)

    # ===================== WATERMARK (BOTH FORMATS) =====================
    def _find_watermark_logo_path():
        candidates = [
            os.path.join(BASE_DIR, "static", "watermark.PNG"),
            os.path.join(BASE_DIR, "static", "watermark.jpg"),
            os.path.join(BASE_DIR, "watermark.PNG"),
            os.path.join(BASE_DIR, "watermark.jpg"),
            os.path.join(BASE_DIR, "UI", "public", "watermark.PNG"),
            os.path.join(BASE_DIR, "UI", "public", "watermark.jpg"),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return None

    def add_footer_watermark(doc_obj, watermark_path: str):
        # Adds a subtle watermark image in the footer (bottom-right) exactly once per document.
        try:
            # Prefer a single footer for the whole document.
            if len(doc_obj.sections) > 1:
                for i in range(1, len(doc_obj.sections)):
                    doc_obj.sections[i].footer.is_linked_to_previous = True

            footer = doc_obj.sections[0].footer

            # Clear existing footer content (avoid stacking / expanding footer height).
            for p in list(footer.paragraphs):
                p._element.getparent().remove(p._element)
            for t in list(footer.tables):
                t._element.getparent().remove(t._element)

            para = footer.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            run = para.add_run()
            run.add_picture(watermark_path, width=Inches(1.0))
        except Exception:
            # Fail-safe: do not break report generation if watermark insertion fails
            pass

    def _enforce_read_only(doc_obj):
        # "Read-only" without password (removable but meets the "if possible" requirement)
        try:
            settings_el = doc_obj.settings.element
            existing = settings_el.xpath("./w:documentProtection")
            dp = existing[0] if existing else OxmlElement("w:documentProtection")
            dp.set(qn("w:edit"), "readOnly")
            dp.set(qn("w:enforcement"), "1")
            if not existing:
                settings_el.append(dp)
        except Exception:
            pass

    watermark_path = _find_watermark_logo_path()
    if watermark_path:
        add_footer_watermark(doc, watermark_path)
    _enforce_read_only(doc)

    metadata = data["metadata"]
    summary = data["summary"]
    rankers = data["rankers"]
    subjects = data["subjects"]
    demographics = data["demographics"]
    centum = data["centum"]

    # ============ HEADER FILL ============
    def replace_header_in_paragraphs(paragraphs):
        for para in paragraphs:
            for run in para.runs:
                text = run.text
                if "Academic Year" in text:
                    run.text = f"Academic Year: {metadata.get('academic_year','')}"
                if "Name of the Program" in text:
                    run.text = f"Name of the Program: {metadata.get('department','')}"
                if "BU Examination month" in text:
                    run.text = f"BU Examination month & year: {metadata.get('exam_session','')}"
                if "Semester" in text:
                    run.text = f"Semester: {metadata.get('semester','')}"
                if "Date of Declaration" in text:
                    run.text = f"Date of Declaration of Result: {metadata.get('result_date','')}"

    # Replace in document body
    replace_header_in_paragraphs(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                replace_header_in_paragraphs(cell.paragraphs)

    # Also replace in page headers (often where this academic info is placed)
    for section in doc.sections:
        replace_header_in_paragraphs(section.header.paragraphs)
        for table in section.header.tables:
            for row in table.rows:
                for cell in row.cells:
                    replace_header_in_paragraphs(cell.paragraphs)



    # ============ SUMMARY TABLE ============
    table = doc.tables[0]
    boys = summary["Boys"]
    girls = summary["Girls"]
    total = summary["Total"]

    def fill_summary_row(row_index, block):
        table.rows[row_index].cells[1].text = str(block["appeared"])
        table.rows[row_index].cells[2].text = str(block["distinction"])
        table.rows[row_index].cells[3].text = str(block["first"])
        table.rows[row_index].cells[4].text = str(block["second"])
        table.rows[row_index].cells[5].text = str(block["pass_class"])
        table.rows[row_index].cells[6].text = str(block["passed"])
        table.rows[row_index].cells[7].text = str(block["failed"])
        table.rows[row_index].cells[8].text = f"{round(block['pass_percentage'],2)}%"
    fill_summary_row(1, boys)
    fill_summary_row(2,girls)
    fill_summary_row(3,total)

    # ============ TOP RANKERS ============
    rank_table = doc.tables[1]
    for i in range(min(3, len(rankers))):
        rank_table.rows[i+1].cells[1].text = rankers[i]["name"]
        rank_table.rows[i+1].cells[2].text = rankers[i]["registrationNo"]
        rank_table.rows[i+1].cells[3].text = str(rankers[i]["marksObtained"])
        rank_table.rows[i+1].cells[4].text = f"{rankers[i]['percentage']}%"

    # ============ SUBJECT TABLE ============
    subject_table = doc.tables[2]
    for i, sub in enumerate(subjects):
        if i + 1 >= len (subject_table.rows):
            break
        row = subject_table.rows[i + 1].cells
        row[0].text = str(sub["slNo"])
        row[1].text = sub["subject"]
        row[2].text = sub["section"]
        row[3].text = sub["faculty"]
        row[4].text = str(sub["passed"])
        row[5].text = str(sub["failed"])
        row[6].text = str(sub["absent"])
        row[7].text = str(sub["centum"])
        row[8].text = f"{sub['passPercent']}%"
        row[9].text = f"{sub['topper']}%"


    # ============ DEMOGRAPHICS TABLE ============
    demo_table = doc.tables[3]

    appeared = demographics["appeared"]
    passed = demographics["passed"]
    passed_60 = demographics["passed_60"]

    def fill_section(section_title, block_data):
        section_row_index = None
        for i, row in enumerate(demo_table.rows):
            row_text = " ".join(cell.text.strip() for cell in row.cells)
            if section_title in row_text:
                section_row_index = i
                break
        if section_row_index is None:
            return
        for i in range(section_row_index + 1, len(demo_table.rows)):
            if demo_table.rows[i].cells[2].text.strip() == "Total":
                row = demo_table.rows[i]
                g_m = block_data.get("GENERAL", {}).get("MALE", 0)
                g_f = block_data.get("GENERAL", {}).get("FEMALE", 0)

                sc_m = block_data.get("SC", {}).get("MALE", 0)
                sc_f = block_data.get("SC", {}).get("FEMALE", 0)

                st_m = block_data.get("ST", {}).get("MALE", 0)
                st_f = block_data.get("ST", {}).get("FEMALE", 0)

                obc_m = block_data.get("OBC", {}).get("MALE", 0)
                obc_f = block_data.get("OBC", {}).get("FEMALE", 0)

            # ---- Fill GENERAL ----
                row.cells[3].text = str(g_m)
                row.cells[4].text = str(g_f)
                row.cells[5].text = "0"

            # ---- Skip EWS (leave blank) ----

            # ---- Fill SC ----
                row.cells[9].text = str(sc_m)
                row.cells[10].text = str(sc_f)
                row.cells[11].text = "0"

            # ---- Fill ST ----
                row.cells[12].text = str(st_m)
                row.cells[13].text = str(st_f)
                row.cells[14].text = "0"

            # ---- Fill OBC ----
                row.cells[15].text = str(obc_m)
                row.cells[16].text = str(obc_f)
                row.cells[17].text = "0"

            # ---- Fill TOTAL ----
                total_m = g_m + sc_m + st_m + obc_m
                total_f = g_f + sc_f + st_f + obc_f

                row.cells[18].text = str(total_m)
                row.cells[19].text = str(total_f)
                row.cells[20].text = "0"

                break


# Apply to all 3 blocks (internal only)
    if download_format != "public":
        fill_section("Total Number of Students Appeared", appeared)
        fill_section("Total Number of Students Passed", passed)
        fill_section("Out of Total", passed_60)
    else:
        # PUBLIC: keep the section + table structure, but render the entire
        # demographics table with empty numeric cells (no 0s, no totals).
        try:
            for row in demo_table.rows:
                for cell in row.cells:
                    if any(ch.isdigit() for ch in cell.text):
                        cell.text = ""
        except Exception:
            pass

        # If the template contains any explicit caste labels in this section,
        # remove them as well (avoid "Caste:" with blank values).
        def scrub_caste_labels(paragraphs):
            for para in paragraphs:
                for run in para.runs:
                    if "caste" in run.text.lower():
                        run.text = ""

        scrub_caste_labels(doc.paragraphs)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    scrub_caste_labels(cell.paragraphs)

    # ============ CENTUM ============
    centum_table = doc.tables[-1]
    
    for i, c in enumerate(centum):
        if i + 1 >= len(centum_table.rows):
            break

        row = centum_table.rows[i+1].cells
        row[0].text = str(i + 1)
        row[1].text = c["name"]
        row[2].text = c["usn"]
        row[3].text = str(c["total"])

    doc.save(output_path)

    return send_file(output_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
