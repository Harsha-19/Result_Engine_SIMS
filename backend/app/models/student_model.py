class Subject:
    def __init__(self, code, name, total, max_marks):
        self.code = code
        self.name = name
        self.total = total
        self.max_marks = max_marks

    def is_failed(self):
        return self.total < (0.4 * self.max_marks)


class Student:
    def __init__(self, usn, name=""):
        self.usn = usn
        self.name = name
        self.subjects = []
        self.overall_total = 0
        self.overall_max = 0
        self.percentage = 0
        self.result = ""

    def add_subject(self, code, name, total, max_marks):
        subject = Subject(code, name, total, max_marks)
        self.subjects.append(subject)

    def calculate_totals(self):
        self.overall_total = sum(sub.total for sub in self.subjects)
        self.overall_max = sum(sub.max_marks for sub in self.subjects)

    def calculate_result(self):
        if self.overall_max == 0:
            self.percentage = 0
            self.result = "FAIL"
            return

        subject_fail = any(sub.is_failed() for sub in self.subjects)

        self.percentage = round((self.overall_total / self.overall_max) * 100, 2)

        if self.percentage >= 40 and not subject_fail:
            self.result = "PASS"
        else:
            self.result = "FAIL"
