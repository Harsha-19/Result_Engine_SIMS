import pdfplumber
pdf_path = r"d:\My Things\PROJECTS\Result_Engine_Main\Result_Engine_SIMS\backend\uploads\result_1774961614_marks.pdf"
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f"--- PAGE {i} ---")
        print(text)
        if i > 0:
            break
