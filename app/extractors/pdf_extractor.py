import pdfplumber
import re
from app.models.student_model import Student


def extract_pdf_data(pdf_path):
    students = []

    # 🔹 Extract full text from PDF
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    # 🔹 Split blocks using USN pattern
    usn_blocks = re.split(r"(U\d{2}[A-Z]{2}\d{2}S\d{4})", full_text)

    for i in range(1, len(usn_blocks), 2):
        usn = usn_blocks[i]
        block = usn_blocks[i + 1]

        student = Student(usn)

        # =========================================================
        # 🔥 NAME EXTRACTION
        # =========================================================
        name_match = re.search(r"Student Name:\s*(.+)", block)

        if name_match:
            raw_line = name_match.group(1).strip()

            raw_line = re.split(
                r"\b(BCA-|BSC/BCA/FAD/ID|BCA/FAD-HIN-4S|BCA/BHM-SAN-4S|BBA\sOE\d+|ENG-OE\d+)",
                raw_line
            )[0].strip()

            raw_line = re.sub(r"\d+\s*\+\s*\d+.*", "", raw_line).strip()
            raw_line = re.sub(r"\b(BSC|BCA|FAD|ID)\b$", "", raw_line).strip()


# 🔹 Pre-compiled patterns for speed
USN_PATTERN = re.compile(r"(U\d{2}[A-Z]{2}\d{2}S\d{4})")
NAME_PATTERN = re.compile(r"Student Name:\s*(.+)")
DIR_JUNK_PATTERN = re.compile(r"\b(BCA-|BSC/BCA/FAD/ID|BCA/FAD-HIN-4S|BCA/BHM-SAN-4S|BBA\sOE\d+|ENG-OE\d+)")
MARK_JUNK_PATTERN = re.compile(r"\d+\s*\+\s*\d+.*")
PROGRAMS_PATTERN = re.compile(r"\b(BSC|BCA|FAD|ID)\b$")
# Combined subject pattern for one-pass extraction
SUBJECT_PARSE_PATTERN = re.compile(r"([A-Z0-9\-\/]+)\s+([A-Z &\-/]+?)\s+(\d+)\s*\+\s*(\d+)\s+0\s+(\d+)\s+(\d+)")

from app.services.performance_utils import measure_performance

@measure_performance
def extract_pdf_data(pdf_path):
    """Memory-efficient PDF extraction with regex-optimized path."""
    students = []
    
    # Use a list for string accumulation (O(n) vs O(n^2))
    text_chunks = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            p_text = page.extract_text()
            if p_text:
                text_chunks.append(p_text)
    
    full_text = "\n".join(text_chunks)
    text_chunks.clear() # Free memory
    
    # SPLIT BY USN
    usn_blocks = USN_PATTERN.split(full_text)
    
    for i in range(1, len(usn_blocks), 2):
        usn = usn_blocks[i]
        block = usn_blocks[i + 1]
        
        student = Student(usn)
        
        # --- NAME EXTRACTION ---
        name_match = NAME_PATTERN.search(block)
        if name_match:
            raw_line = name_match.group(1).strip()
            # Clean junk characters
            raw_line = DIR_JUNK_PATTERN.split(raw_line)[0].strip()
            raw_line = MARK_JUNK_PATTERN.sub("", raw_line).strip()
            raw_line = PROGRAMS_PATTERN.sub("", raw_line).strip()

            student.name = raw_line
        else:
            student.name = ""


        # =========================================================
        # 🔥 SUBJECT + MARKS EXTRACTION (CORRECT VERSION)
        # =========================================================
        subject_pattern = re.findall(
            r"([A-Z0-9\-\/]+)\s+([A-Z &\-/]+?)\s+(\d+)\s*\+\s*(\d+)\s+0\s+(\d+)\s+(\d+)",
            block
        )

        for code, subject_name, cia, see, max_marks, total in subject_pattern:
            cia = int(cia)
            see = int(see)
            max_marks = int(max_marks)
            total = int(total)

            # Use actual max_marks from PDF
            student.add_subject(code, subject_name.strip(), total, max_marks)

        # =========================================================
        # 🔥 CALCULATE TOTALS
        # =========================================================
        student.calculate_totals()
        student.calculate_result()

        # --- SUBJECT EXTRACTION ---
        subjects_found = SUBJECT_PARSE_PATTERN.findall(block)
        for code, sub_name, cia, see, max_m, tot in subjects_found:
            student.add_subject(code, sub_name.strip(), int(tot), int(max_m))

        # --- CALCULATE ---
        student.calculate_totals()
        student.calculate_result()
        students.append(student)

    return students


# =========================================================
# 🔥 Helper: Get Clean Subject Title For Analysis
# =========================================================
def get_clean_subject_title(subject):
    """
    Returns a clean subject title for subject-wise grouping.
    Removes unwanted prefixes and normalizes LAB names.
    """

    name = subject.name.strip()

    # Normalize LAB subjects
    if "LAB" in name.upper():
        name = name.replace("LAB4", "LAB")
        name = name.replace("LAB 4", "LAB")

    # Remove multiple spaces
    name = re.sub(r"\s+", " ", name)

    return name
