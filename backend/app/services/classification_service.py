class ResultClassifier:
    @staticmethod
    def classify(cgpa: float) -> str:
        """
        Determine the classification based on CGPA according to new university rules.
        Classification Rules:
        CGPA >= 8.0 -> Distinction
        CGPA >= 6.0 and < 8.0 -> First Class
        CGPA >= 5.0 and < 6.0 -> Second Class
        CGPA >= 4.0 and < 5.0 -> Pass Class
        CGPA < 4.0 -> Fail
        """
        if cgpa >= 8.0:
            return "Distinction"
        elif cgpa >= 6.0:
            return "First Class"
        elif cgpa >= 5.0:
            return "Second Class"
        elif cgpa >= 4.0:
            return "Pass Class"
        else:
            return "Fail"
