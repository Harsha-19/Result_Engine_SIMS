def get_overall_centum(students):
    """
    Returns students who scored full overall marks.
    """

    centum_students = []

    for student in students:
        if student.overall_total == student.overall_max:
            centum_students.append(student)

    return centum_students
