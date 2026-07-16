from app.services.classification_service import ResultClassifier

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
        
        # Marks
        self.overall_total = 0
        self.overall_max = 0
        self.percentage = 0
        
        # Academic 
        self.sgpa = 0.0
        self.cgpa = 0.0
        self.result = ""
        self.classification = ""
        
        # Metadata
        self.batch_year = None
        self.program = ""
        self.semester = ""

    def add_subject(self, code, name, total, max_marks):
        subject = Subject(code, name, total, max_marks)
        self.subjects.append(subject)

    def calculate_totals(self):
        self.overall_total = sum(sub.total for sub in self.subjects)
        self.overall_max = sum(sub.max_marks for sub in self.subjects)

    def calculate_percentage(self):
        if self.overall_max == 0:
            self.percentage = 0
        else:
            self.percentage = round((self.overall_total / self.overall_max) * 100, 2)

    def calculate_classification(self):
        if self.result == "PASS":
            self.classification = ResultClassifier.classify(self.cgpa)
        else:
            self.classification = "Fail"

    def calculate_result(self):
        self.calculate_totals()
        self.calculate_percentage()
        
        if self.overall_max == 0:
            self.result = "FAIL"
            self.calculate_classification()
            return

        subject_fail = any(sub.is_failed() for sub in self.subjects)

        if self.percentage >= 40 and not subject_fail:
            self.result = "PASS"
        else:
            self.result = "FAIL"
            
        self.calculate_classification()
