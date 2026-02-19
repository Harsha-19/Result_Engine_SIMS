def generate_summary(students, gender_map):
    summary = {
        "Boys": init_block(),
        "Girls": init_block(),
        "Total": init_block(),
    }

    for student in students:
        gender = gender_map.get(student.usn, "NA")

        if gender.lower() in ["male", "m"]:
            category = "Boys"
        elif gender.lower() in ["female", "f"]:
            category = "Girls"
        else:
            category = None

        # Always update Total
        update_counts(summary["Total"], student)

        if category:
            update_counts(summary[category], student)

    # Calculate pass percentage
    for key in summary:
        block = summary[key]
        if block["appeared"] > 0:
            block["pass_percentage"] = (
                block["passed"] / block["appeared"]
            ) * 100
        else:
            block["pass_percentage"] = 0

    return summary


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


def update_counts(block, student):
    block["appeared"] += 1

    if student.result == "PASS":
        block["passed"] += 1

        if student.percentage >= 85:
            block["distinction"] += 1
        elif student.percentage >= 60:
            block["first"] += 1
        elif student.percentage >= 50:
            block["second"] += 1
        elif student.percentage >= 40:
            block["pass_class"] += 1

    elif student.result == "FAIL":
        block["failed"] += 1
    else:
        block["na"] += 1
