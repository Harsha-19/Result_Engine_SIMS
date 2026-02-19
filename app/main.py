import sys
import pandas as pd
import re
from app.extractors.pdf_extractor import extract_pdf_data
from app.services.summary_service import generate_summary
import pdfplumber
from datetime import datetime

def extract_pdf_metadata(pdf_path):
    metadata = {
        "academic_year": "",
        "department": "",
        "semester": "",
        "exam_session": "",
        "result_date": ""
    }

    with pdfplumber.open(pdf_path) as pdf:
        text = ""
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
        r'Semester:\s*([IVX]+)',
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
        except:
            metadata["result_date"] = ""

    # ================= ACADEMIC YEAR =================
    year_match = re.search(r'\d{4}', metadata["exam_session"])

    if year_match:
        year = int(year_match.group())
        metadata["academic_year"] = f"{year-1}-{str(year)[-2:]}"

    return metadata



def extract_excel_data(excel_path):
    df_raw = pd.read_excel(excel_path, header=None)

    header_row_index = None

    # Detect header row containing USN
    for i in range(len(df_raw)):
        row_values = df_raw.iloc[i].astype(str).str.upper()
        if any("USN" in cell for cell in row_values):
            header_row_index = i
            break

    if header_row_index is None:
        raise ValueError("USN column not found in Excel file")

    df = pd.read_excel(excel_path, header=header_row_index)

    usn_col = None
    gender_col = None

    for col in df.columns:
        if "USN" in str(col).upper():
            usn_col = col
        if "GENDER" in str(col).upper():
            gender_col = col

    if usn_col is None:
        raise ValueError("USN column not found after header detection")

    gender_map = {}

    for _, row in df.iterrows():
        usn = str(row[usn_col]).strip()
        gender = str(row[gender_col]).strip() if gender_col else "NA"
        gender_map[usn] = gender

    return set(gender_map.keys()), gender_map

# API INTERFACE
# API INTERFACE
def process_results(pdf_path, excel_path, ui_meta=None):
    metadata = extract_pdf_metadata(pdf_path)

    metadata = {
        "academic_year": ui_meta.get("academic_year", "") if ui_meta else "",
        "department": ui_meta.get("department", "") if ui_meta else "",
        "exam_session": ui_meta.get("exam_session", "") if ui_meta else "",
        "semester": ui_meta.get("semester", "") if ui_meta else "",
        "result_date": ui_meta.get("result_date", "") if ui_meta else "",
    }

    students = extract_pdf_data(pdf_path)
    excel_usns, gender_map = extract_excel_data(excel_path)

    filtered_students = [
        s for s in students if s.usn.strip() in excel_usns
    ]

    for s in filtered_students:
        s.calculate_result()

    # ================= 1. OVERALL SUMMARY =================
    summary = generate_summary(filtered_students, gender_map)

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
    from collections import defaultdict

    subject_data = defaultdict(list)

    official_subjects = {
        "GANAKA KANNADA": "Kannada",
        "HINDI": "Hindi",
        "SANSKRIT": "Sanskrit",
        "INTERNET TECHNOLOGIES LAB": "Internet Technologies Lab",
        "INTERNET TECHNOLOGIES": "Internet Technologies",
        "DESIGN AND ANALYSIS OF ALGORITHM LAB": "ADA Lab",
        "DESIGN AND ANALYSIS OF ALGORITHM": "ADA",
        "PERSONAL WEALTH MANAGEMENT": "Personal Wealth Management",
        "SOFTWARE ENGINEERING": "Software Engineering",
        "COMPUTER ASSEMBLY AND REPAIR": "CAR",
    }

    for student in filtered_students:
        for sub in student.subjects:
            name = sub.name.upper().strip()
            for key in official_subjects:
                if key in name:
                    subject_data[official_subjects[key]].append(sub)
                    break

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
    raw_df = pd.read_excel(excel_path, header=None)

    header_row_index = None
    for i in range(len(raw_df)):
        row_values = raw_df.iloc[i].astype(str).str.upper()
        if any("USN" in cell for cell in row_values):
            header_row_index = i
            break

    caste_df = pd.read_excel(excel_path, header=header_row_index)
    caste_df.columns = caste_df.columns.str.upper().str.strip()

    usn_column = next(col for col in caste_df.columns if "USN" in col)

    caste_map = {}
    for _, row in caste_df.iterrows():
        caste_map[str(row[usn_column]).strip()] = {
            "gender": str(row["GENDER"]).strip().upper(),
            "category": str(row["CATEGORY"]).strip().upper(),
        }

    categories = ["GENERAL", "SC", "ST", "OBC"]
    genders = ["MALE", "FEMALE"]

    def init_block():
        return {cat: {g: 0 for g in genders} for cat in categories}

    appeared = init_block()
    passed = init_block()
    passed_60 = init_block()

    for student in filtered_students:
        usn = student.usn.strip()
        if usn not in caste_map:
            continue

        raw_category = caste_map[usn]["category"]
        raw_gender = caste_map[usn]["gender"]

        if "SCHEDULED CASTE" in raw_category:
            category = "SC"
        elif "SCHEDULED TRIBE" in raw_category:
            category = "ST"
        elif "CATEGORY" in raw_category:
            category = "OBC"
        elif "GENERAL" in raw_category:
            category = "GENERAL"
        else:
            continue

        if raw_gender in ["M", "MALE"]:
            gender = "MALE"
        elif raw_gender in ["F", "FEMALE"]:
            gender = "FEMALE"
        else:
            continue

        appeared[category][gender] += 1

        if student.result == "PASS":
            passed[category][gender] += 1

        if student.result == "PASS" and student.percentage >= 60:
            passed_60[category][gender] += 1

    demographics = {
        "appeared": appeared,
        "passed": passed,
        "passed_60": passed_60
    }

    # ================= 5. CENTUM =================
    centum_list = []
    for student in filtered_students:
        if student.overall_total == student.overall_max and student.overall_max > 0:
            centum_list.append({
                "name": student.name,
                "usn": student.usn,
                "total": student.overall_total
            })

    total_students = len(filtered_students)

    return {
        "metadata": metadata,
        "total": total_students,
        "summary": summary,
        "rankers": rankers,
        "subjects": subject_list,
        "demographics": demographics,
        "centum": centum_list
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

    # Step 3: Filter matching students
    filtered_students = [
        s for s in students if s.usn.strip() in excel_usns
    ]

    # Step 4: Calculate result for each student
    for s in filtered_students:
        s.calculate_result()

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

    summary = generate_summary(filtered_students, gender_map)

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

    #  Official subject mapping
    official_subjects = {
        "GANAKA KANNADA": "Kannada",
        "HINDI": "Hindi",
        "SANSKRIT": "Sanskrit",
        "INTERNET TECHNOLOGIES LAB": "Internet Technologies Lab",
        "INTERNET TECHNOLOGIES": "Internet Technologies",
        "DESIGN AND ANALYSIS OF ALGORITHM LAB": "ADA Lab",
        "DESIGN AND ANALYSIS OF ALGORITHM": "ADA",
        "PERSONAL WEALTH MANAGEMENT": "Personal Wealth Management",
        "SOFTWARE ENGINEERING": "Software Engineering",
        "COMPUTER ASSEMBLY AND REPAIR": "CAR",
    }

    #  Group subjects using official mapping only
    for student in filtered_students:
        for sub in student.subjects:
            name = sub.name.upper().strip()

            for key in official_subjects:
                if key in name:
                    subject_data[official_subjects[key]].append(sub)
                    break

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
    # Detect header row dynamically
    raw_df = pd.read_excel(excel_path, header=None)
    header_row_index = None
    for i in range(len(raw_df)):
        row_values = raw_df.iloc[i].astype(str).str.upper()
        if any("USN" in cell for cell in row_values):
            header_row_index = i
            break
    if header_row_index is None:
        raise ValueError("USN column not found in caste.xlsx")
    caste_df = pd.read_excel(excel_path, header=header_row_index)
    caste_df.columns = caste_df.columns.str.upper().str.strip()

    caste_df.columns = caste_df.columns.str.upper().str.strip()


    # Auto-detect USN column safely
    usn_column = None
    for col in caste_df.columns:
        if "USN" in col:
            usn_column = col
            break

    if usn_column is None:
        raise ValueError("USN column not found in caste.xlsx")

    caste_map = {}

    for _, row in caste_df.iterrows():
        usn = str(row[usn_column]).strip()
        caste_map[usn] = {
            "gender": str(row["GENDER"]).strip().upper(),
            "category": str(row["CATEGORY"]).strip().upper(),
        }

    categories = ["GENERAL", "SC", "ST", "OBC"]


    genders = ["MALE", "FEMALE"]

    def init_block():
        return {cat: {g: 0 for g in genders} for cat in categories}

    appeared = init_block()
    passed = init_block()
    passed_60 = init_block()

    for student in filtered_students:
        usn = student.usn.strip()

        if usn not in caste_map:
            continue

        data = caste_map[usn]
        raw_category = data["category"].strip().upper()
        if "SCHEDULED CASTE" in raw_category:
            category = "SC"
        elif "SCHEDULED TRIBE" in raw_category:
            category = "ST"
        elif "CATEGORY I" in raw_category \
            or "CATEGORY II" in raw_category \
            or "CATEGORY III" in raw_category:
            category = "OBC"
        elif "GENERAL" in raw_category:
            category = "GENERAL"
        else:
            continue



        raw_gender = data["gender"]

        # Normalize gender safely
        if raw_gender in ["M", "MALE"]:
            gender = "MALE"
        elif raw_gender in ["F", "FEMALE"]:
            gender = "FEMALE"
        elif raw_gender in ["T", "TRANS", "TRANSGENDER"]:
            gender = "TRANS"
        else:
            continue

        if category not in categories:
            continue

        # Appeared
        appeared[category][gender] += 1

        # Passed
        if student.result == "PASS":
            passed[category][gender] += 1

        # Passed with 60%+
        if student.result == "PASS" and student.percentage >= 60:
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
    print_block("Out of Total, Students Passed with 60% or above:", passed_60)
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
