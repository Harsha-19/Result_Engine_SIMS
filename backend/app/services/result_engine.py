from app.services.report_generator import generate_report

def process_result(pdf_path, gender_map, header_data):
    students = extract_pdf_data(pdf_path)

    summary = generate_summary(students, gender_map)

    centum_students = get_overall_centum(students)

    output_path = "outputs/final_report.pdf"

    generate_report(header_data, summary, centum_students, output_path)

    return {
        "summary": summary,
        "centum": centum_students,
        "output": output_path
    }
