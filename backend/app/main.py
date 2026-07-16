import sys
import time
import pandas as pd
import json
import re
from app.extractors.pdf_extractor import extract_pdf_data
from app.services.summary_service import generate_summary
import pdfplumber
from datetime import datetime

def normalize_usn(value):
    return re.sub(
        r"[^A-Z0-9]",
        "",
        str(value).upper().strip()
    )

def extract_joining_year(usn: str):
    """
    Dynamically extracts the joining year from a USN.
    Example: U03KU24S0126 -> 24
    """
    if not usn: return None
    match = re.search(r"U\d{2}[A-Z]{2}(\d{2})S\d+", str(usn).upper().strip())
    if match:
        return int(match.group(1))
    return None

from app.services.performance_utils import measure_performance, ResultCache, get_file_stats, logger

@measure_performance
def extract_pdf_metadata(pdf_path):
    print("START extract_pdf_metadata", flush=True)
    logger.info("Entering extract_pdf_metadata")
    # Check cache first
    cache_key = f"meta_{get_file_stats(pdf_path)}"
    cached = ResultCache.get(cache_key)
    if cached:
        logger.info("Leaving extract_pdf_metadata")
        return cached["data"]

    metadata = {
        "academic_year": "",
        "department": "",
        "semester": "",
        "exam_session": "",
        "result_date": ""
    }

    with pdfplumber.open(pdf_path) as pdf:
        text = ""


        # Only check first 2 pages for metadata to save time

        for page in pdf.pages[:2]:
            text += page.extract_text() or ""

    text = text.replace("\n", " ")
    text_upper = text.upper()


    # ================= PROGRAM =================
    program_match = re.search(
        r'Program:\s*([A-Za-z\s]+?)\s+Semester:',
        text,
        re.IGNORECASE
    )

    if program_match:
        metadata["department"] = program_match.group(1).strip()

    # ================= SEMESTER =================
    semester_match = re.search(
        r'Semester:\s*([A-Za-z0-9]+)',
        text,
        re.IGNORECASE
    )

    if semester_match:
        metadata["semester"] = semester_match.group(1).strip()

    # ================= EXAM MONTH =================
    exam_match = re.search(
        r'Exam Month:\s*([A-Z/]+/\d{4})',
        text_upper
    )

    if exam_match:
        metadata["exam_session"] = exam_match.group(1).title()

    # ================= PRINT DATE =================
    print_date_match = re.search(
        r'Print Date:\s*(\d{1,2}/\d{1,2}/\d{4})',
        text
    )

    if print_date_match:
        raw_date = print_date_match.group(1)

        try:
            formatted_date = datetime.strptime(raw_date, "%m/%d/%Y")
            metadata["result_date"] = formatted_date.strftime("%Y-%m-%d")
        except ValueError as e:
            logger.warning(f"Failed to parse print date {raw_date}: {e}")
            metadata["result_date"] = ""

    # ================= ACADEMIC YEAR =================
    year_match = re.search(r'\d{4}', metadata["exam_session"])

    if year_match:
        year = int(year_match.group())
        metadata["academic_year"] = f"{year-1}-{str(year)[-2:]}"

    logger.info("Leaving extract_pdf_metadata")
    print("END extract_pdf_metadata", flush=True)
    return metadata

@measure_performance
def extract_excel_data(excel_path):
    print("START extract_excel_data", flush=True)
    logger.info("Entering extract_excel_data")
    start = time.time()
    cache_key = f"excel_{get_file_stats(excel_path)}"
    cached = ResultCache.get(cache_key)
    if cached:
        logger.info(f"Execution time: {time.time()-start}")
        logger.info("Leaving extract_excel_data")
        return cached["data"]

    # 1. Automatically detect the actual header row (Scan first 10 rows)
    df_preview = pd.read_excel(excel_path, header=None, nrows=10)
    header_row_index = None

    for i in range(len(df_preview)):
        row_values = df_preview.iloc[i].astype(str).str.upper()
        if any(keyword in str(cell) for cell in row_values for keyword in ["USN", "REG", "ROLL", "STUDENT"]):
            header_row_index = i
            break

    if header_row_index is None:
        raise ValueError("Could not detect a valid header row containing USN, REG, ROLL, or STUDENT in the first 10 rows.")

    logger.info(f"Excel Header detected at row index: {header_row_index}")

    # Read the full Excel file using the detected header
    df = pd.read_excel(excel_path, header=header_row_index)

    # 1. Rows completely dynamic: drop completely empty rows
    df.dropna(how='all', inplace=True)

    # 2. Columns completely dynamic: clean column names
    df.columns = df.columns.astype(str).str.upper().str.strip().str.replace(r"\s+", " ", regex=True)
    column_names = df.columns.tolist()

    # Dynamic header detection
    usn_col = next((c for c in df.columns if any(k in str(c) for k in ["USN", "REG", "ROLL"])), None)
    gender_col = next((c for c in df.columns if any(k in str(c) for k in ["GENDER", "SEX"])), None)
    cat_col = next((c for c in df.columns if any(k in str(c) for k in ["CATEGORY", "CASTE", "RESERVATION", "CAT"])), None)
    name_col = next((c for c in df.columns if any(k in str(c) for k in ["NAME", "STUDENT"])), None)

    if usn_col is None:
        raise ValueError("USN column not found in headers")

    # 3. Automatically detect Number of subjects (columns that are not standard metadata)
    standard_cols = {usn_col, gender_col, cat_col, name_col}
    subject_cols = [c for c in df.columns if c not in standard_cols]

    # 3. Automatically detect Number of students
    num_students = len(df)
    
    logger.info(f"Excel Parsed -> Students: {num_students}, Subjects: {len(subject_cols)}, Columns: {column_names}")
    logger.info("Excel parsed.")

    student_data_map = {}

    for _, row in df.iterrows():
        raw_usn = normalize_usn(row[usn_col])
        if not raw_usn or raw_usn == "NAN":
            continue
        
        # Store completely dynamic columns
        student_data = {col: str(row[col]).strip() for col in df.columns}
        
        # Preserve existing keys for backend business logic compatibility
        student_data["gender"] = str(row[gender_col]).strip().upper() if gender_col else "NA"
        student_data["category"] = str(row[cat_col]).strip().upper() if cat_col else "NA"
        
        student_data_map[raw_usn] = student_data

    student_data_map = {
        normalize_usn(k): v
        for k, v in student_data_map.items()
    }
    excel_usns = {
        normalize_usn(usn)
        for usn in student_data_map.keys()
    }
    res = (excel_usns, student_data_map)
    logger.info(f"Execution time: {time.time()-start}")
    logger.info("Leaving extract_excel_data")
    print("END extract_excel_data", flush=True)
    return res

# API INTERFACE

# API INTERFACE
@measure_performance
def process_results(pdf_path, excel_path, ui_meta=None):
    print("START process_results", flush=True)
    logger.info("Entering process_results")
    start = time.time()
    # Global Cache Key based on both files
    cache_key = f"full_{get_file_stats(pdf_path)}_{get_file_stats(excel_path)}"
    
    cached_core = ResultCache.get(cache_key)
    
    if cached_core:
        data = cached_core
    else:
        # Not in cache, perform full extraction
        metadata = extract_pdf_metadata(pdf_path)
        students = extract_pdf_data(pdf_path)
        
        # --- DIAGNOSTIC LOGS START ---
        print("\n========== RAW SUBJECTS FROM PDF ==========\n")
        for student in students:
            print(f"USN: {student.usn}")
            for subject in student.subjects:
                print(f"    {repr(subject.name)}")

        print("\n========== UNIQUE SUBJECTS DETECTED ==========\n")
        unique_subjects = sorted({
            subject.name.strip()
            for student in students
            for subject in student.subjects
        })
        for subject in unique_subjects:
            print(f"- {subject}")
        print(f"\nTotal Unique Subjects: {len(unique_subjects)}")

        print("\n========== SUBJECT COUNT ==========\n")
        for student in students:
            print(f"{student.usn} -> {len(student.subjects)} subjects")
        # --- DIAGNOSTIC LOGS END ---

        excel_usns, student_data_map = extract_excel_data(excel_path)

        # STEP 4: DYNAMIC BATCH FILTERING AND BUILD PDF LOOKUP
        joining_years = {}
        for s in students:
            yr = extract_joining_year(s.usn)
            if yr is not None:
                joining_years[yr] = joining_years.get(yr, 0) + 1

        current_batch = max(joining_years.keys()) if joining_years else None

        regular_students = []
        backlog_students = []
        ignored_usns = []

        for s in students:
            yr = extract_joining_year(s.usn)
            if yr == current_batch:
                regular_students.append(s)
            else:
                backlog_students.append(s)
                ignored_usns.append(s.usn)

        pdf_map = {
            normalize_usn(s.usn): s
            for s in regular_students
        }

        # STEP 5: MATCH USING EXCEL
        filtered_students = []
        missing_students = []

        for usn in excel_usns:
            if usn in pdf_map:
                student = pdf_map[usn]
                student.usn = usn
                filtered_students.append(student)
            else:
                missing_students.append(usn)

        # STEP 6: VALIDATION COUNTS
        logger.info(f"Excel Students: {len(excel_usns)}")
        logger.info(f"PDF Students: {len(pdf_map)}")
        logger.info(f"Matched Students: {len(filtered_students)}")
        logger.info(f"Missing Students: {len(missing_students)}")

        logger.info("Matching complete.")
        for s in filtered_students:
            s.calculate_result()
        
        # Extract gender_map for existing summary_service compatibility
        gender_map = {usn: info["gender"] for usn, info in student_data_map.items()}
        
        # Add Excel count to metadata
        metadata["excelStudentCount"] = len(excel_usns)
        
        data = {
            "raw_metadata": metadata,
            "students": filtered_students,
            "student_data_map": student_data_map,
            "gender_map": gender_map,
            "excel_usns": list(excel_usns),
            "validation": {
                "excelStudents": len(excel_usns),
                "pdfStudents": len(students),
                "regularStudents": len(regular_students),
                "backlogStudents": len(backlog_students),
                "matchedStudents": len(filtered_students),
                "missingStudents": len(missing_students),
                "missingStudentsList": missing_students,
                "currentBatch": current_batch,
                "joiningYears": joining_years,
                "ignoredUsns": ignored_usns
            }
        }
        ResultCache.set(cache_key, data)

    # ---------------------------------------------------------
    # PRINT DYNAMIC VALIDATION TO TERMINAL (FOR THE USER TO SEE)
    # ---------------------------------------------------------
    val = data.get("validation", {})
    print("\n" + "="*40)
    print("      DYNAMIC BATCH & MATCHING VALIDATION")
    print("="*40)
    print(f"Detected Joining Years:\n{json.dumps(val.get('joiningYears', {}), indent=2)}")
    print(f"Detected Current Batch:  {val.get('currentBatch', 'N/A')}")
    print(f"Students Before Filter:  {val.get('pdfStudents', 0)}")
    print(f"Students After Filter:   {val.get('regularStudents', 0)}")
    print(f"Ignored Students:        {val.get('backlogStudents', 0)}")
    
    ignored = val.get('ignoredUsns', [])
    if ignored:
        print(f"Ignored USNs:\n{json.dumps(ignored, indent=2)}")
        
    print("-" * 40)
    print(f"Excel Students (Master): {val.get('excelStudents', 0)}")
    print(f"Matched Students:        {val.get('matchedStudents', 0)}")
    print(f"Missing Students:        {val.get('missingStudents', 0)}")
    print("="*40 + "\n", flush=True)
    # ---------------------------------------------------------

    # Apply UI_META dynamically (No re-parsing!)
    metadata = {
        "academic_year": ui_meta.get("academic_year", "") if ui_meta else data["raw_metadata"]["academic_year"],
        "department": ui_meta.get("department", "") if ui_meta else data["raw_metadata"]["department"],
        "exam_session": ui_meta.get("exam_session", "") if ui_meta else data["raw_metadata"]["exam_session"],
        "semester": ui_meta.get("semester", "") if ui_meta else data["raw_metadata"]["semester"],
        "result_date": ui_meta.get("result_date", "") if ui_meta else data["raw_metadata"]["result_date"],
        "excelStudentCount": data["raw_metadata"].get("excelStudentCount", len(data.get("excel_usns", [])))
    }
    
    filtered_students = data["students"]
    gender_map = data["gender_map"]
    
    logger.info(f"DEBUG: Processing {len(filtered_students)} students for demographics")
    

    # ================= 1. OVERALL SUMMARY =================
    summary, dashboard_summary = generate_summary(filtered_students, gender_map)

    # ================= 2. TOP RANKERS =================
    ranked_students = sorted(
        filtered_students,
        key=lambda x: x.overall_total,
        reverse=True
    )

    rankers = []
    for i, student in enumerate(ranked_students[:3]):
        rankers.append({
            "rank": i + 1,
            "name": student.name,
            "registrationNo": student.usn,
            "marksObtained": student.overall_total,
            "percentage": round(student.percentage, 2)
        })

    # ================= 3. SUBJECT-WISE =================
    # --- DIAGNOSTIC LOGS START ---
    print("\n========== PROCESS_RESULTS: SUBJECT COUNT BEFORE AGGREGATION ==========\n")
    for student in filtered_students:
        print(f"{student.usn} -> {len(student.subjects)} subjects")
    # --- DIAGNOSTIC LOGS END ---

    from collections import defaultdict

    subject_data = defaultdict(list)

    for student in filtered_students:
        for sub in student.subjects:
            name = sub.name.strip().title()
            subject_data[name].append(sub)

    subject_list = []
    sl_no = 1

    for subject_name, subjects in subject_data.items():
        max_marks = subjects[0].max_marks
        appeared = len(subjects)
        passed = 0
        failed = 0
        absent = 0
        centum = 0
        highest = 0

        for sub in subjects:
            if sub.total == 0:
                absent += 1
            elif sub.is_failed():
                failed += 1
            else:
                passed += 1

            if sub.total == max_marks:
                centum += 1

            if sub.total > highest:
                highest = sub.total

        # ================== FIXED SECTION & FACULTY INJECTION ==================
        section = ""
        faculty = ""

        if ui_meta and "subjects" in ui_meta:
            for meta in ui_meta["subjects"]:
                if meta.get("subject", "").strip().lower() == subject_name.strip().lower():
                    section = meta.get("section", "")
                    faculty = meta.get("faculty", "")
                    break
        # =======================================================================

        subject_list.append({
            "id": sl_no,
            "slNo": sl_no,
            "subject": subject_name,
            "section": section,
            "faculty": faculty,
            "passed": passed,
            "failed": failed,
            "absent": absent,
            "centum": centum,
            "passPercent": round((passed / appeared * 100), 2) if appeared else 0,
            "topper": round((highest / max_marks * 100), 2) if max_marks else 0
        })

        sl_no += 1

    # ================= 4. DEMOGRAPHICS =================

    # REUSE the student_data_map from earlier extraction instead of re-reading file
    caste_map = data["student_data_map"]
    
    # DYNAMIC DISCOVERY OF CATEGORIES AND GENDERS
    discovered_categories = set()
    discovered_genders = set()
    for usn, student_meta in caste_map.items():
        if "category" in student_meta:
            cat = student_meta["category"].replace(".", "").replace(" ", "").upper()
            if cat: discovered_categories.add(cat)
        if "gender" in student_meta:
            gen = student_meta["gender"].replace(" ", "").upper()
            if gen: discovered_genders.add(gen)
            
    categories = sorted(list(discovered_categories)) if discovered_categories else ["GENERAL", "OBC", "SC", "ST"]
    genders = sorted(list(discovered_genders)) if discovered_genders else ["MALE", "FEMALE"]

    def init_block():
        return {cat: {g: 0 for g in genders} for cat in categories}

    appeared = init_block()
    passed = init_block()
    passed_60 = init_block()

    for student in filtered_students:
        usn = normalize_usn(student.usn)
        if usn not in caste_map:
            continue

        raw_category = caste_map[usn].get("category", "").upper()
        raw_gender = caste_map[usn].get("gender", "").upper()
        
        category = raw_category.replace(".", "").replace(" ", "")
        gender = raw_gender.replace(" ", "")
        
        if not category or not gender or category not in categories or gender not in genders:
            continue

        appeared[category][gender] += 1

        if student.result == "PASS":
            passed[category][gender] += 1
            if student.cgpa >= 6.0:
                passed_60[category][gender] += 1

    logger.info(f"DEBUG: Demographic Mapping Results -> {json.dumps(appeared)}")

    demographics = {
        "appeared": appeared,
        "passed": passed,
        "passed_60": passed_60,
        "meta": {
            "categories": categories,
            "genders": genders
        }
    }

    # ================= 5. CENTUM =================
    centum_list = []
    centum_sl = 1
    for student in filtered_students:
        for sub in student.subjects:
            if sub.total == sub.max_marks and sub.max_marks > 0:
                centum_list.append({
                    "slNo": centum_sl,
                    "name": student.name,
                    "usn": student.usn,
                    "subject": sub.name.strip().title(),
                    "marks": sub.total,
                    "nameMissing": not bool(student.name.strip()) or student.name.strip().lower() in ["unknown student", "nan", "na"]
                })
                centum_sl += 1

    total_students = len(filtered_students)

    logger.info(f"Execution time: {time.time()-start}")
    logger.info("Leaving process_results")
    print("END process_results", flush=True)

    # --- DIAGNOSTIC LOGS START ---
    print("\n=================================================")
    print(f"Students Parsed:\n{len(filtered_students)}")
    total_subjects = sum(len(student.subjects) for student in filtered_students)
    print(f"\nTotal Subject Entries:\n{total_subjects}")
    unique_subs = sorted({
        subject.name.strip()
        for student in filtered_students
        for subject in student.subjects
    })
    print(f"\nUnique Subjects:\n{len(unique_subs)}")
    print("\nSubject Names:")
    for sub in unique_subs:
        print(f"- {sub}")
    print("=================================================\n")
    # --- DIAGNOSTIC LOGS END ---
    print("\n========== SUBJECT RESPONSE ==========\n")
    print(type(subject_list))
    print(len(subject_list))
    for subject in subject_list:
        print(subject)
    
    return {
        "metadata": metadata,
        "total": total_students,
        "summary": summary,
        "dashboard_summary": dashboard_summary,
        "rankers": rankers,
        "subjects": subject_list,
        "demographics": demographics,
        "centum": centum_list,
        "validation": data.get("validation", {})
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: python -m app.main <marks.pdf> <students.xlsx>")
        return

    pdf_path = sys.argv[1]
    excel_path = sys.argv[2]

    # Step 1: Extract students from PDF
    students = extract_pdf_data(pdf_path)

    # Step 2: Extract USN + Gender from Excel
    excel_usns, gender_map = extract_excel_data(excel_path)

    # Step 3: Filter matching students (Excel is master) and exclude older batches
    joining_years = {}
    for s in students:
        yr = extract_joining_year(s.usn)
        if yr is not None:
            joining_years[yr] = joining_years.get(yr, 0) + 1

    current_batch = max(joining_years.keys()) if joining_years else None

    regular_students = []
    backlog_students = []
    ignored_usns = []

    for s in students:
        yr = extract_joining_year(s.usn)
        if yr == current_batch:
            regular_students.append(s)
        else:
            backlog_students.append(s)
            ignored_usns.append(s.usn)

    pdf_map = {
        normalize_usn(s.usn): s
        for s in regular_students
    }

    filtered_students = []
    missing_students = []

    for usn in excel_usns:
        if usn in pdf_map:
            student = pdf_map[usn]
            student.usn = usn
            filtered_students.append(student)
        else:
            missing_students.append(usn)

    # Step 4: Calculate result for each student
    for s in filtered_students:
        s.calculate_result()

    print("\n--- Validation ---")
    print(f"Detected Joining Years:\n{json.dumps(joining_years, indent=2)}")
    print(f"Detected Current Batch: {current_batch}")
    print(f"Students Before Filter: {len(students)}")
    print(f"Students After Filter: {len(regular_students)}")
    print(f"Ignored Students: {len(backlog_students)}")
    if ignored_usns:
        print(f"Ignored USNs:\n{json.dumps(ignored_usns, indent=2)}")
    print("-" * 40)
    print(f"Excel Students: {len(excel_usns)}")
    print(f"Total PDF Students: {len(students)}")
    print(f"Matched Students: {len(filtered_students)}")
    print(f"Missing Students: {len(missing_students)}")

    print("\n--- Filtered Students ---\n")

    for s in filtered_students:
        print(f"USN: {s.usn}")
        print(f"Name: {s.name}")
        print(f"Overall Total: {s.overall_total}")
        print(f"Overall Max: {s.overall_max}")
        print(f"Percentage: {round(s.percentage, 2)}")
        print(f"Result: {s.result}")
        print("Subjects:")
        for sub in s.subjects:
            print(f"  {sub.code} - {sub.name} → {sub.total}/{sub.max_marks}")
        print("-" * 40)

    # ================= OVERALL SUMMARY =================

    summary, _ = generate_summary(filtered_students, gender_map)

    print("\n================ OVERALL SUMMARY ================\n")

    header = (
        f"{'Category':<10}"
        f"{'Appeared':<10}"
        f"{'Dist':<8}"
        f"{'First':<8}"
        f"{'Second':<8}"
        f"{'PassCls':<8}"
        f"{'Passed':<8}"
        f"{'Failed':<8}"
        f"{'NA':<6}"
        f"{'Pass %':<8}"
    )

    print(header)
    print("-" * len(header))

    for category in ["Boys", "Girls", "Total"]:
        block = summary[category]

        print(
            f"{category:<10}"
            f"{block['appeared']:<10}"
            f"{block['distinction']:<8}"
            f"{block['first']:<8}"
            f"{block['second']:<8}"
            f"{block['pass_class']:<8}"
            f"{block['passed']:<8}"
            f"{block['failed']:<8}"
            f"{block['na']:<6}"
            f"{round(block['pass_percentage'], 2)}%".ljust(8)
        )

    print("\n=================================================\n")

    # ================= TOP RANKERS =================

    print("\n================ TOP RANKERS ================\n")

    ranked_students = sorted(
        filtered_students,
        key=lambda x: x.overall_total,
        reverse=True
    )

    top_students = ranked_students[:3]
    rank_labels = ["I", "II", "III"]

    header = (
        f"{'Rank':<6}"
        f"{'Name':<25}"
        f"{'Registration No.':<18}"
        f"{'Marks Obtained':<18}"
        f"{'Percentage':<12}"
    )

    print(header)
    print("-" * len(header))

    for i, student in enumerate(top_students):
        print(
            f"{rank_labels[i]:<6}"
            f"{student.name.upper():<25}"
            f"{student.usn:<18}"
            f"{student.overall_total:<18}"
            f"{round(student.percentage):<12}"
        )

    print("\n=============================================\n")

        # ================= SUBJECT-WISE ANALYSIS =================

    print("\n================ SUBJECT-WISE ANALYSIS ================\n")

    from collections import defaultdict

    subject_data = defaultdict(list)

    #  Group subjects dynamically
    for student in filtered_students:
        for sub in student.subjects:
            name = sub.name.strip().title()
            subject_data[name].append(sub)
    header = (
        f"{'SL':<4}"
        f"{'Subject Title':<35}"
        f"{'Section':<10}"
        f"{'Faculty Name':<20}"
        f"{'Passed':<8}"
        f"{'Failed':<8}"
        f"{'Absent':<8}"
        f"{'Centum':<8}"
        f"{'Pass %':<10}"
        f"{'Topper %':<10}"
    )

    print(header)
    print("-" * len(header))

    sl_no = 1

    for subject_name, subjects in subject_data.items():

        max_marks = subjects[0].max_marks

        appeared = len(subjects)
        passed = 0
        failed = 0
        absent = 0
        centum = 0
        highest = 0

        for sub in subjects:

            if sub.total == 0:
                absent += 1
            elif sub.is_failed():
                failed += 1
            else:
                passed += 1

            if sub.total == max_marks:
                centum += 1

            if sub.total > highest:
                highest = sub.total

        pass_percentage = (passed / appeared * 100) if appeared > 0 else 0
        topper_percentage = (highest / max_marks * 100) if max_marks > 0 else 0

        print(
            f"{sl_no:<4}"
            f"{subject_name:<35}"
            f"{'':<10}"
            f"{'':<20}"
            f"{passed:<8}"
            f"{failed:<8}"
            f"{absent:<8}"
            f"{centum:<8}"
            f"{round(pass_percentage,2):<10}"
            f"{round(topper_percentage,2):<10}"
        )

        sl_no += 1

    print("\n========================================================\n")

        # ================= IV. PERFORMANCE ANALYSIS BY DEMOGRAPHICS =================

    print("\n================ IV. PERFORMANCE ANALYSIS BY DEMOGRAPHICS ================\n")

    # Load caste.xlsx (already passed as excel_path)
    # REUSE the student_data_map from earlier extraction instead of re-reading file
    caste_map = gender_map

    # DYNAMIC DISCOVERY OF CATEGORIES AND GENDERS
    discovered_categories = set()
    discovered_genders = set()
    for usn, student_meta in caste_map.items():
        if "category" in student_meta:
            cat = student_meta["category"].replace(".", "").replace(" ", "").upper()
            if cat: discovered_categories.add(cat)
        if "gender" in student_meta:
            gen = student_meta["gender"].replace(" ", "").upper()
            if gen: discovered_genders.add(gen)
            
    categories = sorted(list(discovered_categories)) if discovered_categories else ["GENERAL", "OBC", "SC", "ST"]
    genders = sorted(list(discovered_genders)) if discovered_genders else ["MALE", "FEMALE"]

    def init_block():
        return {cat: {g: 0 for g in genders} for cat in categories}

    appeared = init_block()
    passed = init_block()
    passed_60 = init_block()

    for student in filtered_students:
        usn = normalize_usn(student.usn)

        if usn not in caste_map:
            continue

        raw_category = caste_map[usn].get("category", "").upper()
        raw_gender = caste_map[usn].get("gender", "").upper()
        
        category = raw_category.replace(".", "").replace(" ", "")
        gender = raw_gender.replace(" ", "")
        
        if not category or not gender or category not in categories or gender not in genders:
            continue

        # Appeared
        appeared[category][gender] += 1

        # Passed
        if student.result == "PASS":
            passed[category][gender] += 1

        # Passed with First Class+
        if student.result == "PASS" and student.cgpa >= 6.0:
            passed_60[category][gender] += 1

    def print_block(title, block):
        print(f"\n{title}\n")   
        print(f"{'':<10}", end="")
        for cat in categories:
            print(f"{cat:<10}", end="")
        print()
        print("-" * (10 + 10 * len(categories)))
        for gender in genders:
            print(f"{gender.capitalize():<10}", end="")
            total_row = 0
            for cat in categories:
                value = block[cat][gender]
                total_row += value
                print(f"{value:<10}", end="")
            print()
        print("-" * (10 + 10 * len(categories)))
        print(f"{'Total':<10}", end="")
        for cat in categories:
            total_col = sum(block[cat][g] for g in genders)
            print(f"{total_col:<10}", end="")
        print()
    print_block("Total Number of Students Appeared:", appeared)
    print_block("Total Number of Students Passed:", passed)
    print_block("Students Passed with First Class or Above (CGPA >= 6.00):", passed_60)
    print("\n==========================================================================\n")


        # ================= V. CENTUM ACHIEVERS =================

    print("\n================ V. CENTUM ACHIEVERS ================\n")

    header = (
        f"{'Sl.No':<8}"
        f"{'Name':<25}"
        f"{'Registration No.':<20}"
        f"{'Total Marks':<35}"
    )

    print(header)
    print("-" * len(header))

    sl_no = 1
    centum_found = False

    for student in filtered_students:
        for sub in student.subjects:
            if sub.total == sub.max_marks and sub.max_marks > 0:
                centum_found = True

                print(
                    f"{sl_no:<8}"
                    f"{student.name:<25}"
                    f"{student.usn:<20}"
                    f"{sub.name:<35}"
                )

                sl_no += 1

    if not centum_found:
        print("No centum achievers found.")

    print("\n=====================================================\n")

if __name__ == "__main__":
    main()
