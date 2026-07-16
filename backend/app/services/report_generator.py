from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib import fonts
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


def generate_report(header_data, summary, centum_students, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # =========================================================
    # 🔹 HEADER SECTION (Dynamic)
    # =========================================================

    elements.append(Paragraph(f"<b>{header_data['trust_name']}</b>", styles["Normal"]))
    elements.append(Paragraph(f"<b>{header_data['institute_name']}</b>", styles["Title"]))
    elements.append(Paragraph(header_data["address"], styles["Normal"]))
    elements.append(Paragraph(header_data["recognition"], styles["Normal"]))
    elements.append(Paragraph(header_data["accreditation"], styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(
        Paragraph(
            f"<b>Academic Year:</b> {header_data['academic_year']} &nbsp;&nbsp;&nbsp; "
            f"<b>Program:</b> {header_data['program_name']}",
            styles["Normal"],
        )
    )

    elements.append(
        Paragraph(
            f"<b>Exam:</b> {header_data['exam_month_year']} &nbsp;&nbsp;&nbsp; "
            f"<b>Semester:</b> {header_data['semester']}",
            styles["Normal"],
        )
    )

    elements.append(
        Paragraph(
            f"<b>Date of Declaration:</b> {header_data['result_declaration_date']}",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 0.5 * inch))

    # =========================================================
    # 🔹 I. OVERALL SUMMARY
    # =========================================================

    elements.append(Paragraph("<b>I. Overall Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    table_data = [
        [
            "Category",
            "Appeared",
            "Distinction\n(CGPA ≥ 8.00)",
            "First Class\n(CGPA 6.00-7.99)",
            "Second Class\n(CGPA 5.00-5.99)",
            "Pass Class\n(CGPA 4.00-4.99)",
            "Total Passed",
            "Total Failed",
            "Pass %",
        ]
    ]

    for category in ["Boys", "Girls", "Total"]:
        block = summary[category]
        table_data.append(
            [
                category,
                block["appeared"],
                block["distinction"],
                block["first"],
                block["second"],
                block["pass_class"],
                block["passed"],
                block["failed"],
                f"{block['pass_percentage']:.2f}",
            ]
        )

    summary_table = Table(table_data, repeatRows=1)
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ]
        )
    )

    elements.append(summary_table)

    elements.append(Spacer(1, 0.5 * inch))

    # =========================================================
    # 🔹 V. OVERALL CENTUM ACHIEVERS (Modified Requirement)
    # =========================================================

    elements.append(Paragraph("<b>Overall Centum Achievers</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    if centum_students:
        centum_data = [["Sl.No", "Name", "Registration No", "Total Marks"]]

        for i, student in enumerate(centum_students, start=1):
            centum_data.append(
                [
                    i,
                    student.name,
                    student.usn,
                    student.overall_total,
                ]
            )

        centum_table = Table(centum_data, repeatRows=1)
        centum_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ALIGN", (0, 1), (-1, -1), "CENTER"),
                ]
            )
        )

        elements.append(centum_table)
    else:
        elements.append(Paragraph("No Overall Centum Achievers.", styles["Normal"]))

    doc.build(elements)
