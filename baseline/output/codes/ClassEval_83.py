import sqlite3

class StudentDatabaseProcessor:
    """
    This is a class with database operation, including inserting student information, searching for student information by name, and deleting student information by name.
    """

    def __init__(self, database_name):
        """
        Initializes the StudentDatabaseProcessor object with the specified database name.
        :param database_name: str, the name of the SQLite database.
        """
        self.database_name = database_name
        self.conn = sqlite3.connect(self.database_name)
        self.cursor = self.conn.cursor()

    def create_student_table(self):
        """
        Creates a "students" table in the database if it does not exist already.Fields include ID of type int, name of type str, age of type int, gender of type str, and grade of type int
        :return: None
        >>> processor = StudentDatabaseProcessor("students.db")
        >>> processor.create_student_table()
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                grade INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

    def insert_student(self, student_data):
        """
        Inserts a new student into the "students" table.
        :param student_data: dict, a dictionary containing the student's information (name, age, gender, grade).
        :return: None
        >>> processor = StudentDatabaseProcessor("students.db")
        >>> processor.create_student_table()
        >>> student_data = {'name': 'John', 'age': 15, 'gender': 'Male', 'grade': 9}
        >>> processor.insert_student(student_data)
        """
        self.cursor.execute('''
            INSERT INTO students (name, age, gender, grade)
            VALUES (?, ?, ?, ?)
        ''', (student_data['name'], student_data['age'], student_data['gender'], student_data['grade']))
        self.conn.commit()

    def search_student_by_name(self, name):
        """
        Searches for a student in the "students" table by their name.
        :param name: str, the name of the student to search for.
        :return: list of tuples, the rows from the "students" table that match the search criteria.
        >>> processor = StudentDatabaseProcessor("students.db")
        >>> processor.create_student_table()
        >>> result = processor.search_student_by_name("John")
        """
        self.cursor.execute('''
            SELECT * FROM students WHERE name = ?
        ''', (name,))
        return self.cursor.fetchall()

    def delete_student_by_name(self, name):
        """
        Deletes a student from the "students" table by their name.
        :param name: str, the name of the student to delete.
        :return: None
        >>> processor = StudentDatabaseProcessor("students.db")
        >>> processor.create_student_table()
        >>> student_data = {'name': 'John', 'age': 15, 'gender': 'Male', 'grade': 9}
        >>> processor.insert_student(student_data)
        >>> processor.delete_student_by_name("John")
        """
        self.cursor.execute('''
            DELETE FROM students WHERE name = ?
        ''', (name,))
        self.conn.commit()

import unittest


class StudentDatabaseProcessorTestInsertStudent(unittest.TestCase):
    def setUp(self):
        self.processor = StudentDatabaseProcessor("test_database.db")
        self.processor.create_student_table()

    def tearDown(self):
        conn = sqlite3.connect("test_database.db")
        conn.execute("DROP TABLE IF EXISTS students")
        conn.commit()
        conn.close()

    def test_insert_student_1(self):
        student_data = {
            'name': 'Alice',
            'age': 20,
            'gender': 'female',
            'grade': 90
        }
        self.processor.insert_student(student_data)

        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name=?", ('Alice',))
        result = cursor.fetchall()
        conn.close()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 'Alice')

    def test_insert_student_2(self):
        student_data = {
            'name': 'aaa',
            'age': 20,
            'gender': 'female',
            'grade': 90
        }
        self.processor.insert_student(student_data)

        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name=?", ('aaa',))
        result = cursor.fetchall()
        conn.close()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 'aaa')

    def test_insert_student_3(self):
        student_data = {
            'name': 'bbb',
            'age': 20,
            'gender': 'female',
            'grade': 90
        }
        self.processor.insert_student(student_data)

        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name=?", ('bbb',))
        result = cursor.fetchall()
        conn.close()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 'bbb')

    def test_insert_student_4(self):
        student_data = {
            'name': 'ccc',
            'age': 20,
            'gender': 'female',
            'grade': 90
        }
        self.processor.insert_student(student_data)

        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name=?", ('ccc',))
        result = cursor.fetchall()
        conn.close()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 'ccc')

    def test_insert_student_5(self):
        student_data = {
            'name': 'ddd',
            'age': 20,
            'gender': 'female',
            'grade': 90
        }
        self.processor.insert_student(student_data)

        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name=?", ('ddd',))
        result = cursor.fetchall()
        conn.close()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 'ddd')


class StudentDatabaseProcessorTestSearchStudentByName(unittest.TestCase):
    def setUp(self):
        self.processor = StudentDatabaseProcessor("test_database.db")
        self.processor.create_student_table()

    def tearDown(self):
        conn = sqlite3.connect("test_database.db")
        conn.execute("DROP TABLE IF EXISTS students")
        conn.commit()
        conn.close()

    def test_search_student_by_name_1(self):
        student_data = {
            'name': 'Bob',
            'age': 19,
            'gender': 'male',
            'grade': 85
        }
        self.processor.insert_student(student_data)

        result = self.processor.search_student_by_name('Bob')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 'Bob')

    def test_search_student_by_name_2(self):
        student_data = {
            'name': 'aaa',
            'age': 19,
            'gender': 'male',
            'grade': 85
        }
        self.processor.insert_student(student_data)

        result = self.processor.search_student_by_name('aaa')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 'aaa')

    def test_search_student_by_name_3(self):
        student_data = {
            'name': 'bbb',
            'age': 19,
            'gender': 'male',
            'grade': 85
        }
        self.processor.insert_student(student_data)

        result = self.processor.search_student_by_name('bbb')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 'bbb')

    def test_search_student_by_name_4(self):
        student_data = {
            'name': 'ccc',
            'age': 19,
            'gender': 'male',
            'grade': 85
        }
        self.processor.insert_student(student_data)

        result = self.processor.search_student_by_name('ccc')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 'ccc')

    def test_search_student_by_name_5(self):
        student_data = {
            'name': 'ddd',
            'age': 19,
            'gender': 'male',
            'grade': 85
        }
        self.processor.insert_student(student_data)

        result = self.processor.search_student_by_name('ddd')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 'ddd')


class StudentDatabaseProcessorTestDeleteStudentByName(unittest.TestCase):
    def setUp(self):
        self.processor = StudentDatabaseProcessor("test_database.db")
        self.processor.create_student_table()

    def tearDown(self):
        conn = sqlite3.connect("test_database.db")
        conn.execute("DROP TABLE IF EXISTS students")
        conn.commit()
        conn.close()

    def test_delete_student_by_name_1(self):
        student_data = {
            'name': 'Charlie',
            'age': 18,
            'gender': 'male',
            'grade': 95
        }
        self.processor.insert_student(student_data)

        self.processor.delete_student_by_name('Charlie')

        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name=?", ('Charlie',))
        result = cursor.fetchall()
        conn.close()

        self.assertEqual(len(result), 0)

    def test_delete_student_by_name_2(self):
        student_data = {
            'name': 'aaa',
            'age': 18,
            'gender': 'male',
            'grade': 95
        }
        self.processor.insert_student(student_data)

        self.processor.delete_student_by_name('aaa')

        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name=?", ('aaa',))
        result = cursor.fetchall()
        conn.close()

        self.assertEqual(len(result), 0)

    def test_delete_student_by_name_3(self):
        student_data = {
            'name': 'bbb',
            'age': 18,
            'gender': 'male',
            'grade': 95
        }
        self.processor.insert_student(student_data)

        self.processor.delete_student_by_name('bbb')

        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name=?", ('bbb',))
        result = cursor.fetchall()
        conn.close()

        self.assertEqual(len(result), 0)

    def test_delete_student_by_name_4(self):
        student_data = {
            'name': 'ccc',
            'age': 18,
            'gender': 'male',
            'grade': 95
        }
        self.processor.insert_student(student_data)

        self.processor.delete_student_by_name('ccc')

        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name=?", ('ccc',))
        result = cursor.fetchall()
        conn.close()

        self.assertEqual(len(result), 0)

    def test_delete_student_by_name_5(self):
        student_data = {
            'name': 'ddd',
            'age': 18,
            'gender': 'male',
            'grade': 95
        }
        self.processor.insert_student(student_data)

        self.processor.delete_student_by_name('ddd')

        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name=?", ('ddd',))
        result = cursor.fetchall()
        conn.close()

        self.assertEqual(len(result), 0)


class StudentDatabaseProcessorTest(unittest.TestCase):
    def setUp(self):
        self.processor = StudentDatabaseProcessor("test_database.db")
        self.processor.create_student_table()

    def tearDown(self):
        conn = sqlite3.connect("test_database.db")
        conn.execute("DROP TABLE IF EXISTS students")
        conn.commit()
        conn.close()

    def test_StudentDatabaseProcessor(self):
        student_data = {
            'name': 'Alice',
            'age': 20,
            'gender': 'female',
            'grade': 90
        }
        self.processor.insert_student(student_data)

        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name=?", ('Alice',))
        result = cursor.fetchall()
        conn.close()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 'Alice')

        student_data = {
            'name': 'Bob',
            'age': 19,
            'gender': 'male',
            'grade': 85
        }
        self.processor.insert_student(student_data)

        result = self.processor.search_student_by_name('Bob')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 'Bob')

        student_data = {
            'name': 'Charlie',
            'age': 18,
            'gender': 'male',
            'grade': 95
        }
        self.processor.insert_student(student_data)

        self.processor.delete_student_by_name('Charlie')

        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name=?", ('Charlie',))
        result = cursor.fetchall()
        conn.close()

        self.assertEqual(len(result), 0)