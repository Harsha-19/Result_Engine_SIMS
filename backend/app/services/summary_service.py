def generate_summary(students, gender_map):
    summary = {
        "Boys": init_block(),
        "Girls": init_block(),
        "Total": init_block(),
    }

    # Flat summary for direct dashboard render
    flat_summary = {
        "regular_students": len(students),
        "boys": 0,
        "girls": 0,
        "distinction": 0,
        "first_class": 0,
        "second_class": 0,
        "pass_class": 0,
        "passed": 0,
        "failed": 0,
        "overall_pass_percentage": 0.00
    }

    for student in students:
        gender = gender_map.get(student.usn, "NA")

        if gender.lower() in ["male", "m"]:
            category = "Boys"
            flat_summary["boys"] += 1
        elif gender.lower() in ["female", "f"]:
            category = "Girls"
            flat_summary["girls"] += 1
        else:
            category = None

        # Always update Total
        update_counts(summary["Total"], student, flat_summary)

        if category:
            update_counts(summary[category], student, None)

    # Validation
    if flat_summary["passed"] + flat_summary["failed"] != flat_summary["regular_students"]:
        raise ValueError("Result Analysis Mismatch")

    if flat_summary["regular_students"] > 0:
        flat_summary["overall_pass_percentage"] = round((flat_summary["passed"] / flat_summary["regular_students"]) * 100, 2)

    # Calculate pass percentage for old format
    for key in summary:
        block = summary[key]
        if block["appeared"] > 0:
            block["pass_percentage"] = round((block["passed"] / block["appeared"]) * 100, 2)
        else:
            block["pass_percentage"] = 0

    return summary, flat_summary


def init_block():
    return {
        "appeared": 0,
        "distinction": 0,
        "first": 0,
        "second": 0,
        "pass_class": 0,
        "passed": 0,
        "failed": 0,
        "na": 0,
        "pass_percentage": 0,
    }


def update_counts(block, student, flat_summary=None):
    block["appeared"] += 1

    if student.result == "PASS":
        block["passed"] += 1
        if flat_summary is not None:
            flat_summary["passed"] += 1

        if student.classification == "Distinction":
            block["distinction"] += 1
            if flat_summary is not None: flat_summary["distinction"] += 1
        elif student.classification == "First Class":
            block["first"] += 1
            if flat_summary is not None: flat_summary["first_class"] += 1
        elif student.classification == "Second Class":
            block["second"] += 1
            if flat_summary is not None: flat_summary["second_class"] += 1
        elif student.classification == "Pass Class":
            block["pass_class"] += 1
            if flat_summary is not None: flat_summary["pass_class"] += 1

    elif student.result == "FAIL":
        block["failed"] += 1
        if flat_summary is not None:
            flat_summary["failed"] += 1
    else:
        block["na"] += 1
