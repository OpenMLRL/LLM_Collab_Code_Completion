class HRManagementSystem:
    """
    This is a class as personnel management system that implements functions such as adding, deleting, querying, and updating employees
    """

    def __init__(self):
        """
        Initialize the HRManagementSystem with an attribute employees, which is an empty dictionary.
        """
        self.employees = {}

    def add_employee(self, employee_id, name, position, department, salary):
        """
        Add a new employee to the HRManagementSystem.
        :param employee_id: The employee's id, int.
        :param name: The employee's name, str.
        :param position: The employee's position, str.
        :param department: The employee's department, str.
        :param salary: The employee's salary, int.
        :return: If the employee is already in the HRManagementSystem, returns False, otherwise, returns True.
        >>> hrManagementSystem = HRManagementSystem()
        >>> hrManagementSystem.add_employee(1, 'John', 'Manager', 'Sales', 100000)
        True
        >>> hrManagementSystem.add_employee(1, 'John', 'Manager', 'Sales', 100000)
        False
        """
        if employee_id in self.employees:
            return False
        self.employees[employee_id] = {
            'name': name,
            'position': position,
            'department': department,
            'salary': salary
        }
        return True

    def remove_employee(self, employee_id):
        """
        Remove an employee from the HRManagementSystem.
        :param employee_id: The employee's id, int.
        :return: If the employee is already in the HRManagementSystem, returns True, otherwise, returns False.
        >>> hrManagementSystem = HRManagementSystem()
        >>> hrManagementSystem.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        >>> hrManagementSystem.remove_employee(1)
        True
        >>> hrManagementSystem.remove_employee(2)
        False
        """
        if employee_id in self.employees:
            del self.employees[employee_id]
            return True
        return False

    def update_employee(self, employee_id: int, employee_info: dict):
        """
        Update an employee's information in the HRManagementSystem.
        :param employee_id: The employee's id, int.
        :param employee_info: The employee's information, dict.
        :return: If the employee is already in the HRManagementSystem, returns True, otherwise, returns False.
        >>> hrManagementSystem = HRManagementSystem()
        >>> hrManagementSystem.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        >>> hrManagementSystem.update_employee(1, {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 20000})
        True
        >>> hrManagementSystem.update_employee(2, {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 20000})
        False
        """
        if employee_id not in self.employees:
            return False
        self.employees[employee_id].update(employee_info)
        return True

    def get_employee(self, employee_id):
        """
        Get an employee's information from the HRManagementSystem.
        :param employee_id: The employee's id, int.
        :return: If the employee is already in the HRManagementSystem, returns the employee's information, otherwise, returns False.
        >>> hrManagementSystem = HRManagementSystem()
        >>> hrManagementSystem.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        >>> hrManagementSystem.get_employee(1)
        {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}
        >>> hrManagementSystem.get_employee(2)
        False
        """
        return self.employees.get(employee_id, False)

    def list_employees(self):
        """
        List all employees' information in the HRManagementSystem.
        :return: A list of all employees' information, dict.
        >>> hrManagementSystem = HRManagementSystem()
        >>> hrManagementSystem.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        >>> hrManagementSystem.list_employees()
        {1: {'employee_ID': 1, 'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        """
        return {k: {'employee_ID': k, **v} for k, v in self.employees.items()}

import unittest

class HRManagementSystemTestAddEmployee(unittest.TestCase):
    def test_add_employee(self):
        hr_system = HRManagementSystem()
        self.assertEqual(hr_system.add_employee(1, "John Doe", "Manager", "HR", 5000), True)
        self.assertEqual(hr_system.employees[1], {'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000})

    def test_add_employee_2(self):
        hr_system = HRManagementSystem()
        self.assertEqual(hr_system.add_employee(1, "John Doe", "Manager", "HR", 5000), True)
        self.assertEqual(hr_system.add_employee(1, "John Doe", "Manager", "HR", 5000), False)
        self.assertEqual(hr_system.employees[1], {'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000})

    def test_add_employee_3(self):
        hr_system = HRManagementSystem()
        self.assertEqual(hr_system.add_employee(1, "John Doe", "Manager", "HR", 5000), True)
        self.assertEqual(hr_system.add_employee(2, "John Doe", "Manager", "HR", 5000), True)
        self.assertEqual(hr_system.employees,{1: {'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000}, 2: {'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000}})

    def test_add_employee_4(self):
        hr_system = HRManagementSystem()
        self.assertEqual(hr_system.add_employee(1, "John Doe", "Manager", "HR", 5000), True)
        self.assertEqual(hr_system.add_employee(2, "John Doe", "Manager", "HR", 5000), True)
        self.assertEqual(hr_system.add_employee(1, "John Doe", "Manager", "HR", 5000), False)
        self.assertEqual(hr_system.employees,{1: {'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000}, 2: {'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000}})

    def test_add_employee_5(self):
        hr_system = HRManagementSystem()
        self.assertEqual(hr_system.add_employee(1, "John Doe", "Manager", "HR", 5000), True)
        self.assertEqual(hr_system.add_employee(2, "John Doe", "Manager", "HR", 5000), True)
        self.assertEqual(hr_system.add_employee(1, "John Doe", "Manager", "HR", 5000), False)
        self.assertEqual(hr_system.add_employee(2, "John Doe", "Manager", "HR", 5000), False)
        self.assertEqual(hr_system.employees,{1: {'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000}, 2: {'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000}})

class HRManagementSystemTestRemoveEmployee(unittest.TestCase):
    def test_remove_employee(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.remove_employee(1), True)
        self.assertEqual(hr_system.employees, {})

    def test_remove_employee_2(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.remove_employee(1), True)
        self.assertEqual(hr_system.remove_employee(1), False)
        self.assertEqual(hr_system.employees, {})

    def test_remove_employee_3(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}, 2: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.remove_employee(1), True)
        self.assertEqual(hr_system.employees, {2: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}})

    def test_remove_employee_4(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}, 2: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.remove_employee(1), True)
        self.assertEqual(hr_system.remove_employee(2), True)
        self.assertEqual(hr_system.employees, {})

    def test_remove_employee_5(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}, 2: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.remove_employee(1), True)
        self.assertEqual(hr_system.remove_employee(2), True)
        self.assertEqual(hr_system.remove_employee(1), False)
        self.assertEqual(hr_system.remove_employee(2), False)
        self.assertEqual(hr_system.employees, {})

class HRManagementSystemTestUpdateEmployee(unittest.TestCase):
    def test_update_employee(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.update_employee(1, {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 20000}), True)
        self.assertEqual(hr_system.employees[1], {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 20000})

    def test_update_employee_2(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {}
        self.assertEqual(hr_system.update_employee(1, {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 20000}), False)
        self.assertEqual(hr_system.employees, {})

    def test_update_employee_3(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.update_employee(2, {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 20000}), False)
        self.assertEqual(hr_system.employees, {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}})

    def test_update_employee_4(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.update_employee(1, {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 20000}), True)
        self.assertEqual(hr_system.update_employee(1, {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 20000}), True)
        self.assertEqual(hr_system.employees[1], {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 20000})

    def test_update_employee_5(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.update_employee(1, {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 20000}), True)
        self.assertEqual(hr_system.update_employee(1, {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 20000}), True)
        self.assertEqual(hr_system.update_employee(1, {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}), True)
        self.assertEqual(hr_system.employees[1], {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000})

    def test_update_employee_6(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.update_employee(1, {'Name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 20000}), False)


class HRManagementSystemTestGetEmployee(unittest.TestCase):
    def test_get_employee(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.get_employee(1), {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000})

    def test_get_employee_2(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {}
        self.assertEqual(hr_system.get_employee(1), False)

    def test_get_employee_3(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.get_employee(2), False)

    def test_get_employee_4(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.get_employee(1), {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000})
        self.assertEqual(hr_system.get_employee(1), {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000})

    def test_get_employee_5(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}, 2: {'name': 'Jane', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.get_employee(1), {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000})
        self.assertEqual(hr_system.get_employee(2), {'name': 'Jane', 'position': 'Manager', 'department': 'Sales', 'salary': 100000})

class HRManagementSystemTestListEmployees(unittest.TestCase):
    def test_list_employees(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.list_employees(), {1: {'employee_ID':1,'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}})

    def test_list_employees_2(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {}
        self.assertEqual(hr_system.list_employees(), {})

    def test_list_employees_3(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}, 2: {'name': 'Jane', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.list_employees(), {1: {'employee_ID':1,'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}, 2: {'employee_ID':2,'name': 'Jane', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}})

    def test_list_employees_4(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}, 2: {'name': 'Jane', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.list_employees(), {1: {'employee_ID':1,'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}, 2: {'employee_ID':2,'name': 'Jane', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}})
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.list_employees(), {1: {'employee_ID':1,'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}})

    def test_list_employees_5(self):
        hr_system = HRManagementSystem()
        hr_system.employees = {1: {'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}, 2: {'name': 'Jane', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}}
        self.assertEqual(hr_system.list_employees(), {1: {'employee_ID':1,'name': 'John', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}, 2: {'employee_ID':2,'name': 'Jane', 'position': 'Manager', 'department': 'Sales', 'salary': 100000}})
        hr_system.employees = {}
        self.assertEqual(hr_system.list_employees(), {})
class HRManagementSystemTestMain(unittest.TestCase):
    def test_main(self):
        hr_system = HRManagementSystem()
        hr_system.add_employee(1, "John Doe", "Manager", "HR", 5000)
        hr_system.add_employee(2, "Jane Smith", "Developer", "IT", 4000)
        self.assertEqual(hr_system.list_employees(), {1: {'employee_ID': 1, 'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000}, 2: {'employee_ID': 2, 'name': 'Jane Smith', 'position': 'Developer', 'department': 'IT', 'salary': 4000}})
        hr_system.remove_employee(2)
        self.assertEqual(hr_system.list_employees(), {1: {'employee_ID': 1, 'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000}})
        self.assertEqual(hr_system.remove_employee(2), False)
        self.assertEqual(hr_system.update_employee(1, {'name': 'John Doe Jr.', 'salary': 5500}), True)
        self.assertEqual(hr_system.employees[1], {'name': 'John Doe Jr.', 'position': 'Manager', 'department': 'HR', 'salary': 5500})
        self.assertEqual(hr_system.update_employee(3, {'name': 'Invalid Employee'}), False)
        self.assertEqual(hr_system.get_employee(1), {'name': 'John Doe Jr.', 'position': 'Manager', 'department': 'HR', 'salary': 5500})
        self.assertEqual(hr_system.get_employee(2), False)
        self.assertEqual(hr_system.list_employees(), {1: {'employee_ID': 1, 'name': 'John Doe Jr.', 'position': 'Manager', 'department': 'HR', 'salary': 5500}})

    def test_main_2(self):
        hr_system = HRManagementSystem()
        self.assertEqual(hr_system.remove_employee(2), False)
        self.assertEqual(hr_system.update_employee(1, {'name': 'John Doe Jr.', 'salary': 5500}), False)
        hr_system.add_employee(1, "John Doe", "Manager", "HR", 5000)
        hr_system.add_employee(2, "Jane Smith", "Developer", "IT", 4000)
        self.assertEqual(hr_system.list_employees(), {
            1: {'employee_ID': 1, 'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000},
            2: {'employee_ID': 2, 'name': 'Jane Smith', 'position': 'Developer', 'department': 'IT', 'salary': 4000}})
        self.assertEqual(hr_system.remove_employee(2), True)
        self.assertEqual(hr_system.employees, {1: {'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000}})
        self.assertEqual(hr_system.list_employees(), {1: {'employee_ID': 1, 'name': 'John Doe', 'position': 'Manager', 'department': 'HR', 'salary': 5000}})
        self.assertEqual(hr_system.update_employee(1, {'name': 'John Doe Jr.', 'salary': 5500}), True)
        self.assertEqual(hr_system.employees[1], {'name': 'John Doe Jr.', 'position': 'Manager', 'department': 'HR', 'salary': 5500})
        self.assertEqual(hr_system.get_employee(1), {'name': 'John Doe Jr.', 'position': 'Manager', 'department': 'HR', 'salary': 5500})
        self.assertEqual(hr_system.get_employee(2), False)