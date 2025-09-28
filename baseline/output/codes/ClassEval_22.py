class ClassRegistrationSystem:
    """
    This is a class as a class registration system, allowing to register students, register them for classes, retrieve students by major, get a list of all majors, and determine the most popular class within a specific major.
    """

    def __init__(self):
        """
        Initialize the registration system with the attribute students and students_registration_class.
        students is a list of student dictionaries, each student dictionary has the key of name and major.
        students_registration_class is a dictionaries, key is the student name, value is a list of class names
        """
        self.students = []
        self.students_registration_classes = {}

    def register_student(self, student):
        """
        register a student to the system, add the student to the students list, if the student is already registered, return 0, else return 1
        """
        for s in self.students:
            if s['name'] == student['name']:
                return 0
        self.students.append(student)
        self.students_registration_classes[student['name']] = []
        return 1

    def register_class(self, student_name, class_name):
        """
        register a class to the student.
        :param student_name: str
        :param class_name: str
        :return a list of class names that the student has registered
        """
        if student_name not in self.students_registration_classes:
            self.students_registration_classes[student_name] = []
        self.students_registration_classes[student_name].append(class_name)
        return self.students_registration_classes[student_name]

    def get_students_by_major(self, major):
        """
        get all students in the major
        :param major: str
        :return a list of student name
        """
        return [student['name'] for student in self.students if student['major'] == major]

    def get_all_major(self):
        """
        get all majors in the system
        :return a list of majors
        """
        return list({student['major'] for student in self.students})

    def get_most_popular_class_in_major(self, major):
        """
        get the class with the highest enrollment in the major.
        :return  a string of the most popular class in this major
        """
        students_in_major = self.get_students_by_major(major)
        class_enrollments = {}
        for student_name in students_in_major:
            classes = self.students_registration_classes.get(student_name, [])
            for class_name in classes:
                class_enrollments[class_name] = class_enrollments.get(class_name, 0) + 1
        if not class_enrollments:
            return None
        return max(class_enrollments, key=class_enrollments.get)

import unittest


class ClassRegistrationSystemTestRegisterStudent(unittest.TestCase):

    def setUp(self):
        self.registration_system = ClassRegistrationSystem()

    def test_register_student(self):
        student1 = {"name": "John", "major": "Computer Science"}
        self.assertEqual(self.registration_system.register_student(student1), 1)

    def test_register_student2(self):
        student1 = {"name": "John", "major": "Computer Science"}
        self.registration_system.register_student(student1)
        self.assertEqual(self.registration_system.register_student(student1), 0)

    def test_register_student3(self):
        student1 = {"name": "John", "major": "Computer Science"}
        student2 = {"name": "Alice", "major": "Mathematics"}
        self.assertEqual(self.registration_system.register_student(student1), 1)
        self.assertEqual(self.registration_system.register_student(student2), 1)
        self.assertEqual(self.registration_system.register_student(student2), 0)

class ClassRegistrationSystemTestRegisterClass(unittest.TestCase):

    def setUp(self):
        self.registration_system = ClassRegistrationSystem()

    def test_register_class(self):
        self.assertEqual(self.registration_system.register_class(student_name="John", class_name="CS101"), ["CS101"])

    def test_register_class2(self):
        self.registration_system.register_class(student_name="John", class_name="CS101")
        self.registration_system.register_class(student_name="John", class_name="CS102")
        self.assertEqual(self.registration_system.register_class(student_name="John", class_name="CS103"), ["CS101", "CS102", "CS103"])

    def test_register_class3(self):
        self.registration_system.register_class(student_name="John", class_name="CS101")
        self.registration_system.register_class(student_name="Tom", class_name="CS102")
        self.assertEqual(self.registration_system.register_class(student_name="John", class_name="CS103"), ["CS101", "CS103"])


class ClassRegistrationSystemTestGetStudent(unittest.TestCase):

    def setUp(self):
        self.registration_system = ClassRegistrationSystem()

    def test_get_students_by_major(self):
        self.registration_system.students = [{"name": "John", "major": "Computer Science"},
                                             {"name": "Bob", "major": "Computer Science"}]

        cs_students = self.registration_system.get_students_by_major("Computer Science")

        self.assertEqual(cs_students, ["John", "Bob"])

    def test_get_students_by_major2(self):
        self.registration_system.students = [{"name": "John", "major": "Computer Science"},
                                             {"name": "Bob", "major": "Computer Science"}]

        cs_students = self.registration_system.get_students_by_major("Computer Science")
        math_students = self.registration_system.get_students_by_major("Mathematics")

        self.assertEqual(cs_students, ["John", "Bob"])
        self.assertEqual(math_students, [])

    def test_get_students_by_major3(self):
        self.registration_system.students = [{"name": "John", "major": "Computer Science"},
                                             {"name": "Bob", "major": "Computer Science"},
                                                {"name": "Alice", "major": "Mathematics"}]

        cs_students = self.registration_system.get_students_by_major("Computer Science")
        math_students = self.registration_system.get_students_by_major("Mathematics")

        self.assertEqual(cs_students, ["John", "Bob"])
        self.assertEqual(math_students, ["Alice"])

    def test_get_students_by_major4(self):
        self.registration_system.students = [{"name": "John", "major": "Computer Science"},
                                             {"name": "Bob", "major": "Computer Science"},
                                             {"name": "Alice", "major": "Mathematics"},
                                             {"name": "Tom", "major": "Mathematics"},
                                             {"name": "Jerry", "major": "Mathematics"}]

        cs_students = self.registration_system.get_students_by_major("Computer Science")
        math_students = self.registration_system.get_students_by_major("Mathematics")
        self.assertEqual(cs_students, ["John", "Bob"])
        self.assertEqual(math_students, ["Alice", "Tom", "Jerry"])



class ClassRegistrationSystemTestGetMajor(unittest.TestCase):

    def setUp(self):
        self.registration_system = ClassRegistrationSystem()

    def test_get_all_major(self):
        self.registration_system.students = [{"name": "John", "major": "Computer Science"},
                                             {"name": "Bob", "major": "Computer Science"}]

        majors = self.registration_system.get_all_major()

        self.assertEqual(majors, ["Computer Science"])

    def test_get_all_major2(self):
        self.registration_system.students = [{"name": "John", "major": "Computer Science"},
                                             {"name": "Bob", "major": "Computer Science"},
                                             {"name": "Alice", "major": "Mathematics"}]

        majors = self.registration_system.get_all_major()

        self.assertEqual(majors, ["Computer Science", "Mathematics"])

    def test_get_all_major3(self):
        self.registration_system.students = [{"name": "John", "major": "Computer Science"},
                                             {"name": "Bob", "major": "Computer Science"},
                                             {"name": "Alice", "major": "Mathematics"},
                                             {"name": "Tom", "major": "Mathematics"},
                                             {"name": "Jerry", "major": "Physics"}]

        majors = self.registration_system.get_all_major()

        self.assertEqual(majors, ["Computer Science", "Mathematics", "Physics"])

class ClassRegistrationSystemTestPopularClass(unittest.TestCase):

    def setUp(self):
        self.registration_system = ClassRegistrationSystem()

    def test_get_most_popular_class_in_major(self):
        self.registration_system.students = [{"name": "John", "major": "Computer Science"},
                                             {"name": "Bob", "major": "Computer Science"},
                                             {"name": "Alice", "major": "Computer Science"}]

        self.registration_system.students_registration_classes = {"John": ["Algorithms", "Data Structures"],
                                            "Bob": ["Operating Systems", "Data Structures", "Algorithms"],
                                            "Alice": ["Data Structures", "Operating Systems", "Calculus"]}

        cs_most_popular_class = self.registration_system.get_most_popular_class_in_major("Computer Science")

        self.assertEqual(cs_most_popular_class, "Data Structures")

    def test_get_most_popular_class_in_major2(self):
        self.registration_system.students = [{"name": "John", "major": "Computer Science"},
                                                {"name": "Bob", "major": "Computer Science"},
                                                {"name": "Alice", "major": "Computer Science"},
                                                {"name": "Tom", "major": "Mathematics"},
                                                {"name": "Jerry", "major": "Mathematics"}]

        self.registration_system.students_registration_classes = {"John": ["Algorithms", "Data Structures"],
                                                                  "Bob": ["Data Structures", "Algorithms",
                                                                          "Operating Systems"],
                                                                  "Alice": ["Data Structures", "Operating Systems",
                                                                            "Calculus"],
                                                                    "Tom": ["Calculus", "Linear Algebra"],
                                                                    "Jerry": ["Linear Algebra", "Statistics"]}

        cs_most_popular_class = self.registration_system.get_most_popular_class_in_major("Computer Science")
        math_most_popular_class = self.registration_system.get_most_popular_class_in_major("Mathematics")
        self.assertEqual(cs_most_popular_class, "Data Structures")
        self.assertEqual(math_most_popular_class, "Linear Algebra")

class ClassRegistrationSystemTest(unittest.TestCase):

        def setUp(self):
            self.registration_system = ClassRegistrationSystem()

        def test(self):
            student1 = {"name": "John", "major": "Computer Science"}
            student2 = {"name": "Bob", "major": "Computer Science"}
            student3 = {"name": "Alice", "major": "Mathematics"}
            student4 = {"name": "Tom", "major": "Mathematics"}
            self.registration_system.register_student(student1)
            self.registration_system.register_student(student2)
            self.registration_system.register_student(student3)
            self.registration_system.register_student(student4)
            self.registration_system.register_class("John", "Algorithms")
            self.registration_system.register_class("John", "Data Structures")
            self.registration_system.register_class("Bob", "Operating Systems")
            self.registration_system.register_class("Bob", "Data Structures")
            self.assertEqual(self.registration_system.get_students_by_major("Computer Science"), ["John", "Bob"])
            self.assertEqual(self.registration_system.get_students_by_major("Mathematics"), ["Alice", "Tom"])
            self.assertEqual(self.registration_system.get_all_major(), ["Computer Science", "Mathematics"])
            self.assertEqual(self.registration_system.get_most_popular_class_in_major("Computer Science"), "Data Structures")