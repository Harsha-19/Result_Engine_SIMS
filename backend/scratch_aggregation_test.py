from app.main import process_results
import os
import json

def test():
    pdf_path = os.path.join("uploads", "result_1774961614_marks.pdf")
    excel_path = os.path.join("uploads", "caste_5dade069.xlsx") # dummy caste
    print(f"Testing {pdf_path}")
    res = process_results(pdf_path, excel_path)
    
    print("\n========== FINAL API RESPONSE: SUBJECTS ==========\n")
    print(f"Count: {len(res['subjects'])}")
    for sub in res['subjects']:
        print(sub['subject'])

if __name__ == "__main__":
    test()
