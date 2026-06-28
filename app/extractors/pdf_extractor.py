import pdfplumber
import re
import time
from app.models.student_model import Student
from app.services.performance_utils import measure_performance, logger

# 🔹 Pre-compiled patterns for high performance extraction
USN_PATTERN = re.compile(r"(U\d{2}[A-Z]{2}\d{2}S\d{4})")
NAME_PATTERN = re.compile(r"Student Name:\s*(.+)")
DIR_JUNK_PATTERN = re.compile(r"\b(BCA-|BSC/BCA/FAD/ID|BCA/FAD-HIN-4S|BCA/BHM-SAN-4S|BBA\sOE\d+|ENG-OE\d+)")
MARK_JUNK_PATTERN = re.compile(r"\d+\s*\+\s*\d+.*")
PROGRAMS_PATTERN = re.compile(r"\b(BSC|BCA|FAD|ID)\b$")
# Correct subject pattern for extraction
SUBJECT_PARSE_PATTERN = re.compile(r"([A-Z0-9\-\/]+)\s+([A-Z &\-/]+?)\s+(\d+)\s*\+\s*(\d+)\s+0\s+(\d+)\s+(\d+)")

@measure_performance
def extract_pdf_data(pdf_path):
    """Memory-efficient PDF extraction with regex-optimized processing."""
    logger.info("Entering extract_pdf_data")
    start = time.time()
    students = []
    text_chunks = []
    
    # 1. Parallel-ready text extraction
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            p_text = page.extract_text()
            if p_text:
                text_chunks.append(p_text)
    
    full_text = "\n".join(text_chunks)
    text_chunks = None # Clear memory
    
    # 2. Split PDF by USN blocks using optimized regex
    usn_blocks = USN_PATTERN.split(full_text)
    
    # Iterate through blocks (usn, block_content, usn, block_content...)
    for i in range(1, len(usn_blocks), 2):
        usn = usn_blocks[i]
        block = usn_blocks[i + 1]
        
        student = Student(usn)
        
        # --- Optimized Name Extraction ---
        name_match = NAME_PATTERN.search(block)
        if name_match:
            raw_line = name_match.group(1).strip()
            # Multi-stage cleaning for accuracy
            raw_line = DIR_JUNK_PATTERN.split(raw_line)[0].strip()
            raw_line = MARK_JUNK_PATTERN.sub("", raw_line).strip()
            raw_line = PROGRAMS_PATTERN.sub("", raw_line).strip()
            student.name = raw_line
        else:
            student.name = "Unknown Student"

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
        student.calculate_totals()
        student.calculate_result()
        students.append(student)

    logger.info("PDF parsed.")
    logger.info(f"Execution time: {time.time()-start}")
    logger.info("Leaving extract_pdf_data")
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
