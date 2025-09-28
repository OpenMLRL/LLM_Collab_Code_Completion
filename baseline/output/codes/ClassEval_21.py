from datetime import datetime

class Classroom:
    """
    This is a class representing a classroom, capable of adding and removing courses, checking availability at a given time, and detecting conflicts when scheduling new courses.
    """

    def __init__(self, id):
        """
        Initialize the classroom management system.
        :param id: int, the id of classroom
        """
        self.id = id
        self.courses = []

    def add_course(self, course):
        """
        Add course to self.courses list if the course wasn't in it.
        :param course: dict, information of the course, including 'start_time', 'end_time' and 'name'
        >>> classroom = Classroom(1)
        >>> classroom.add_course({'name': 'math', 'start_time': '8:00', 'end_time': '9:40'})
        """
        if course not in self.courses:
            self.courses.append(course)

    def remove_course(self, course):
        """
        Remove course from self.courses list if the course was in it.
        :param course: dict, information of the course, including 'start_time', 'end_time' and 'name'
        >>> classroom = Classroom(1)
        >>> classroom.add_course({'name': 'math', 'start_time': '8:00', 'end_time': '9:40'})
        >>> classroom.add_course({'name': 'math', 'start_time': '8:00', 'end_time': '9:40'})
        """
        if course in self.courses:
            self.courses.remove(course)

    def is_free_at(self, check_time):
        """
        change the time format as '%H:%M' and check the time is free or not in the classroom.
        :param check_time: str, the time need to be checked
        :return: True if the check_time does not conflict with every course time, or False otherwise.
        >>> classroom = Classroom(1)
        >>> classroom.add_course({'name': 'math', 'start_time': '8:00', 'end_time': '9:40'})
        >>> classroom.is_free_at('10:00')
        True
        >>> classroom.is_free_at('9:00')
        False
        """
        check_time = datetime.strptime(check_time, '%H:%M').time()
        for course in self.courses:
            start = datetime.strptime(course['start_time'], '%H:%M').time()
            end = datetime.strptime(course['end_time'], '%H:%M').time()
            if start <= check_time < end:
                return False
        return True

    def check_course_conflict(self, new_course):
        """
        Before adding a new course, check if the new course time conflicts with any other course.
        :param new_course: dict, information of the course, including 'start_time', 'end_time' and 'name'
        :return: False if the new course time conflicts(including two courses have the same boundary time) with other courses, or True otherwise.
        >>> classroom = Classroom(1)
        >>> classroom.add_course({'name': 'math', 'start_time': '8:00', 'end_time': '9:40'})
        >>> classroom.check_course_conflict({'name': 'SE', 'start_time': '9:40', 'end_time': '10:40'})
        False
        """
        new_start = datetime.strptime(new_course['start_time'], '%H:%M').time()
        new_end = datetime.strptime(new_course['end_time'], '%H:%M').time()
        for course in self.courses:
            start = datetime.strptime(course['start_time'], '%H:%M').time()
            end = datetime.strptime(course['end_time'], '%H:%M').time()
            if not (new_end <= start or new_start >= end):
                return False
        return True

import unittest
from datetime import datetime


class ClassroomTestAddCourse(unittest.TestCase):
    def test_add_course_1(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)

    def test_add_course_2(self):
        classroom = Classroom(1)
        course = {'name': 'Chinese', 'start_time': '10:00', 'end_time': '11:00'}
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)

    def test_add_course_3(self):
        classroom = Classroom(1)
        course = {'name': 'English', 'start_time': '11:00', 'end_time': '12:00'}
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)

    def test_add_course_4(self):
        classroom = Classroom(1)
        course = {'name': 'Art', 'start_time': '14:00', 'end_time': '15:00'}
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)

    def test_add_course_5(self):
        classroom = Classroom(1)
        course = {'name': 'P.E.', 'start_time': '15:00', 'end_time': '16:00'}
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)

    def test_add_course_6(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)


class ClassroomTestRemoveCourse(unittest.TestCase):
    def test_remove_course_1(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)

    def test_remove_course_2(self):
        classroom = Classroom(1)
        course = {'name': 'Chinese', 'start_time': '10:00', 'end_time': '11:00'}
        classroom.add_course(course)
        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)

    def test_remove_course_3(self):
        classroom = Classroom(1)
        course = {'name': 'English', 'start_time': '11:00', 'end_time': '12:00'}
        classroom.add_course(course)
        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)

    def test_remove_course_4(self):
        classroom = Classroom(1)
        course = {'name': 'Art', 'start_time': '14:00', 'end_time': '15:00'}
        classroom.add_course(course)
        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)

    def test_remove_course_5(self):
        classroom = Classroom(1)
        course = {'name': 'P.E.', 'start_time': '15:00', 'end_time': '16:00'}
        classroom.add_course(course)
        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)

    def test_remove_course_6(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)


class ClassroomTestIsFreeAt(unittest.TestCase):
    def test_is_free_at_1(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        check_time = '11:00'
        result = classroom.is_free_at(check_time)
        self.assertTrue(result)

    def test_is_free_at_2(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        check_time = '09:30'
        result = classroom.is_free_at(check_time)
        self.assertFalse(result)

    def test_is_free_at_3(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        check_time = '12:00'
        result = classroom.is_free_at(check_time)
        self.assertTrue(result)

    def test_is_free_at_4(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        check_time = '14:00'
        result = classroom.is_free_at(check_time)
        self.assertTrue(result)

    def test_is_free_at_5(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        check_time = '09:40'
        result = classroom.is_free_at(check_time)
        self.assertFalse(result)


class ClassroomTestCheckCourseConflict(unittest.TestCase):
    def test_check_course_conflict_1(self):
        classroom = Classroom(1)
        existing_course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(existing_course)
        new_course = {'name': 'SE', 'start_time': '10:30', 'end_time': '11:30'}
        result = classroom.check_course_conflict(new_course)
        self.assertTrue(result)

    def test_check_course_conflict_2(self):
        classroom = Classroom(1)
        existing_course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(existing_course)
        new_course = {'name': 'SE', 'start_time': '09:30', 'end_time': '10:30'}
        result = classroom.check_course_conflict(new_course)
        self.assertFalse(result)

    # have the same boundary time
    # existing_course['end_time'] == new_course['start_time']
    def test_check_course_conflict_3(self):
        classroom = Classroom(1)
        existing_course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(existing_course)
        new_course = {'name': 'SE', 'start_time': '10:00', 'end_time': '11:30'}
        result = classroom.check_course_conflict(new_course)
        self.assertFalse(result)

    def test_check_course_conflict_4(self):
        classroom = Classroom(1)
        existing_course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(existing_course)
        new_course = {'name': 'SE', 'start_time': '09:40', 'end_time': '10:40'}
        result = classroom.check_course_conflict(new_course)
        self.assertFalse(result)

    def test_check_course_conflict_5(self):
        classroom = Classroom(1)
        existing_course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(existing_course)
        new_course = {'name': 'SE', 'start_time': '14:30', 'end_time': '15:30'}
        result = classroom.check_course_conflict(new_course)
        self.assertTrue(result)

    def test_check_course_conflict_6(self):
        classroom = Classroom(1)
        existing_course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(existing_course)
        new_course = {'name': 'SE', 'start_time': '8:30', 'end_time': '9:30'}
        result = classroom.check_course_conflict(new_course)
        self.assertFalse(result)


class ClassroomTestMain(unittest.TestCase):
    def test_main(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)

        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)

        classroom.add_course(course)
        self.assertIn(course, classroom.courses)
        check_time = '09:30'
        result = classroom.is_free_at(check_time)
        self.assertFalse(result)

        new_course = {'name': 'SE', 'start_time': '09:30', 'end_time': '10:30'}
        result = classroom.check_course_conflict(new_course)
        self.assertFalse(result)