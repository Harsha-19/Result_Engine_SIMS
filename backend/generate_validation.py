import sys
from app.extractors.pdf_extractor import extract_pdf_data

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_validation.py <marks.pdf>")
        return

    pdf_path = sys.argv[1]
    
    print("Extracting data from PDF...")
    students = extract_pdf_data(pdf_path)
    
    print("\n================ VALIDATION REPORT ================\n")
    
    header = (
        f"{'USN':<15}"
        f"{'Name':<25}"
        f"{'SGPA':<8}"
        f"{'CGPA':<8}"
        f"{'Classification':<15}"
        f"{'Result':<8}"
        f"{'Overall Marks':<15}"
        f"{'Percentage':<12}"
    )
    print(header)
    print("-" * len(header))
    
    for student in students:
        print(
            f"{student.usn:<15}"
            f"{student.name[:23]:<25}"
            f"{student.sgpa:<8.2f}"
            f"{student.cgpa:<8.2f}"
            f"{student.classification:<15}"
            f"{student.result:<8}"
            f"{student.overall_total:<15}"
            f"{student.percentage:<12.2f}"
        )
        
    print("\n===================================================\n")

if __name__ == "__main__":
    main()
