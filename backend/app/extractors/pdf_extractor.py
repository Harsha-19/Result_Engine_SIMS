import pdfplumber
import re
import time
from app.models.student_model import Student
from app.services.performance_utils import measure_performance, logger

# 🔹 Pre-compiled patterns for high performance extraction
USN_PATTERN = re.compile(r"(U\d{2}[A-Z]{2}\d{2}S\d{4})")
NAME_PATTERN = re.compile(r"Student Name:\s*(.+)")

# Independent patterns for SGPA and CGPA
SGPA_PATTERN = re.compile(r"SGPA\s*[:=]?\s*([\d\.]+)", re.IGNORECASE)
CGPA_PATTERN = re.compile(r"CGPA\s*[:=]?\s*([\d\.]+)", re.IGNORECASE)

# Correct subject pattern for extraction
SUBJECT_PARSE_PATTERN = re.compile(r"([A-Z0-9\-\/]+)\s+([A-Z &\-/]+?)\s+(\d+)\s*\+\s*(\d+)\s+0\s+(\d+)\s+(\d+)")

@measure_performance
def extract_pdf_data(pdf_path):
    """Memory-efficient PDF extraction with regex-optimized processing."""
    print("START extract_pdf_data", flush=True)
    logger.info("Entering extract_pdf_data")
    start = time.time()
    students = []
    text_chunks = []
    
    # 1. Parallel-ready text extraction
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}", flush=True)
        for i, page in enumerate(pdf.pages):
            p_text = page.extract_text()
            if p_text:
                text_chunks.append(p_text)
            print(f"Extracted page {i+1}/{total_pages}", flush=True)
    
    full_text = "\n".join(text_chunks)
    text_chunks = None # Clear memory
    print("Text extraction complete, starting regex split", flush=True)
    
    # 2. Split PDF by USN blocks using optimized regex
    usn_blocks = USN_PATTERN.split(full_text)
    print(f"Regex split complete, {len(usn_blocks)} blocks found", flush=True)
    
    # Iterate through blocks (usn, block_content, usn, block_content...)
    for i in range(1, len(usn_blocks), 2):
        usn = usn_blocks[i]
        block = usn_blocks[i + 1]
        
        student = Student(usn)
        
        # --- Optimized Name Extraction ---
        name_match = NAME_PATTERN.search(block)
        if name_match:
            raw_line = name_match.group(1).strip()
            sub_match = SUBJECT_PARSE_PATTERN.search(raw_line)
            if sub_match:
                student.name = raw_line[:sub_match.start()].strip()
            else:
                student.name = raw_line
        else:
            student.name = "Unknown Student"
            
        # --- Independent SGPA / CGPA Extraction ---
        sgpa_match = SGPA_PATTERN.search(block)
        if sgpa_match:
            try:
                student.sgpa = float(sgpa_match.group(1))
            except ValueError:
                pass

        cgpa_match = CGPA_PATTERN.search(block)
        if cgpa_match:
            try:
                student.cgpa = float(cgpa_match.group(1))
            except ValueError:
                pass

        # --- Efficient Subject + Marks Extraction ---
        # Single-pass regex parsing
        subjects_found = SUBJECT_PARSE_PATTERN.findall(block)
        for code, sub_name, cia, see, max_m, tot in subjects_found:
            student.add_subject(
                code.strip(), 
                sub_name.strip(), 
                int(tot), 
                int(max_m)
            )

        # Finalize student data
        student.calculate_result()
        students.append(student)

    logger.info("PDF parsed.")
    logger.info(f"Execution time: {time.time()-start}")
    logger.info("Leaving extract_pdf_data")
    print("END extract_pdf_data", flush=True)
    return students

def get_clean_subject_title(subject):
    """Returns a normalized subject title for analysis grouping."""
    name = subject.name.strip()
    # Normalize LAB subjects
    if "LAB" in name.upper():
        name = re.sub(r"LAB\s*\d*", "LAB", name, flags=re.IGNORECASE)
    # Remove multiple spaces
    name = re.sub(r"\s+", " ", name)
    return name
