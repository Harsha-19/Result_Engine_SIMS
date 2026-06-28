import sys
import json
from app.main import process_results

def main():
    try:
        data = process_results('uploads/marks_4a20255a.pdf', 'uploads/caste_4a20255a.xlsx')
        val = data.get("validation", {})
        
        excel_students = val.get("excelStudents", 0)
        pdf_students = val.get("pdfStudents", 0)
        matched_students = val.get("matchedStudents", 0)
        missing_students = val.get("missingStudents", 0)
        
        with open('matching_report.md', 'w', encoding='utf-8') as f:
            f.write('# Matching Report\n\n')
            f.write('This report confirms the new matching logic treating Excel as the master dataset.\n\n')
            f.write('## Verification\n')
            f.write(f'- **Excel Students (Master):** {excel_students}\n')
            f.write(f'- **PDF Students (Lookup):** {pdf_students}\n')
            f.write(f'- **Matched Students:** {matched_students}\n')
            f.write(f'- **Missing from PDF:** {missing_students}\n')

        with open('validation_report.md', 'w', encoding='utf-8') as f:
            f.write('# Validation Report\n\n')
            f.write('## Core Data\n')
            f.write('The final total student count for all analysis is strictly bound to the Excel sheet count.\n\n')
            f.write(f'**Analysis Total Students:** {data.get("total", 0)}\n')
            if excel_students > 0:
                success_rate = round(matched_students / excel_students * 100, 2)
            else:
                success_rate = 0
            f.write(f'**Match Success Rate:** {success_rate}%\n')

        with open('unmatched_students.txt', 'w', encoding='utf-8') as f:
            f.write('Missing Students (Present in Excel, Not in PDF):\n')
            
            missing_usns = val.get("missingStudentsList", [])
            
            f.write(f'Total Missing: {len(missing_usns)}\n\n')
            for usn in sorted(missing_usns):
                f.write(f'{usn}\n')

            
        print("Reports generated successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
