class SQLQueryBuilder:
    """
    This class provides to build SQL queries, including SELECT, INSERT, UPDATE, and DELETE statements. 
    """

    @staticmethod
    def select(table, columns='*', where=None):
        """
        Generate the SELECT SQL statement from the given parameters.
        :param table: str, the query table in database.
        :param columns: list of str, ['col1', 'col2'].
        :param where: dict, {key1: value1, key2: value2 ...}. The query condition.
        return query: str, the SQL query statement.
        >>> SQLQueryBuilder.select('table1', columns = ["col1","col2"], where = {"age": 15})
        "SELECT col1, col2 FROM table1 WHERE age='15'"
        """
        columns_clause = ', '.join(columns) if isinstance(columns, list) else columns
        where_clause = ''
        if where:
            where_conditions = [f"{key}='{value}'" for key, value in where.items()]
            where_clause = ' WHERE ' + ' AND '.join(where_conditions)
        return f"SELECT {columns_clause} FROM {table}{where_clause}"

    @staticmethod
    def insert(table, data):
        """
        Generate the INSERT SQL statement from the given parameters.
        :param table: str, the table to be inserted in database.
        :param data: dict, the key and value in SQL insert statement
        :return query: str, the SQL insert statement.
        >>> SQLQueryBuilder.insert('table1', {'name': 'Test', 'age': 14})
        "INSERT INTO table1 (name, age) VALUES ('Test', '14')"
        """
        columns = ', '.join(data.keys())
        values = ', '.join(f"'{value}'" for value in data.values())
        return f"INSERT INTO {table} ({columns}) VALUES ({values})"

    @staticmethod
    def delete(table, where=None):
        """
        Generate the DELETE SQL statement from the given parameters.
        :param table: str, the table that will be excuted with DELETE operation in database
        :param where: dict, {key1: value1, key2: value2 ...}. The query condition.
        :return query: str, the SQL delete statement.
        >>> SQLQueryBuilder.delete('table1', {'name': 'Test', 'age': 14})
        "DELETE FROM table1 WHERE name='Test' AND age='14'"
        """
        where_clause = ''
        if where:
            where_conditions = [f"{key}='{value}'" for key, value in where.items()]
            where_clause = ' WHERE ' + ' AND '.join(where_conditions)
        return f"DELETE FROM {table}{where_clause}"

    @staticmethod
    def update(table, data, where=None):
        """
        Generate the UPDATE SQL statement from the given parameters.
        :param table: str, the table that will be excuted with UPDATE operation in database
        :param data: dict, the key and value in SQL update statement
        :param where: dict, {key1: value1, key2: value2 ...}. The query condition.
        >>> SQLQueryBuilder.update('table1', {'name': 'Test2', 'age': 15}, where = {'name':'Test'})
        "UPDATE table1 SET name='Test2', age='15' WHERE name='Test'"
        """
        set_clause = ', '.join(f"{key}='{value}'" for key, value in data.items())
        where_clause = ''
        if where:
            where_conditions = [f"{key}='{value}'" for key, value in where.items()]
            where_clause = ' WHERE ' + ' AND '.join(where_conditions)
        return f"UPDATE {table} SET {set_clause}{where_clause}"

import unittest


class SQLQueryBuilderTestSelect(unittest.TestCase):
    def test_select_1(self):
        self.assertEqual(
            SQLQueryBuilder.select('users', ["id", "name"], {'age': 30}),
            "SELECT id, name FROM users WHERE age='30'"
        )

    def test_select_2(self):
        self.assertEqual(
            SQLQueryBuilder.select('students', ["id", "name"], {'age': 18}),
            "SELECT id, name FROM students WHERE age='18'"
        )

    def test_select_3(self):
        self.assertEqual(
            SQLQueryBuilder.select('items', ["id", "name"], {'price': 1.0}),
            "SELECT id, name FROM items WHERE price='1.0'"
        )

    def test_select_4(self):
        self.assertEqual(
            SQLQueryBuilder.select('users', ["id"], {'age': 30}),
            "SELECT id FROM users WHERE age='30'"
        )

    def test_select_5(self):
        self.assertEqual(
            SQLQueryBuilder.select('users', ["name"], {'age': 30}),
            "SELECT name FROM users WHERE age='30'"
        )

    def test_select_6(self):
        self.assertEqual(
            SQLQueryBuilder.select('users', ["name"]),
            "SELECT name FROM users"
        )

    def test_select_7(self):
        self.assertEqual(
            SQLQueryBuilder.select('users', "*"),
            "SELECT * FROM users"
        )


class SQLQueryBuilderTestInsert(unittest.TestCase):
    def test_insert_1(self):
        self.assertEqual(
            SQLQueryBuilder.insert('users', {'name': 'Tom', 'age': 30}),
            "INSERT INTO users (name, age) VALUES ('Tom', '30')"
        )

    def test_insert_2(self):
        self.assertEqual(
            SQLQueryBuilder.insert('students', {'name': 'Tom', 'age': 18}),
            "INSERT INTO students (name, age) VALUES ('Tom', '18')"
        )

    def test_insert_3(self):
        self.assertEqual(
            SQLQueryBuilder.insert('items', {'name': 'apple', 'price': 1.0}),
            "INSERT INTO items (name, price) VALUES ('apple', '1.0')"
        )

    def test_insert_4(self):
        self.assertEqual(
            SQLQueryBuilder.insert('users', {'name': 'Tom'}),
            "INSERT INTO users (name) VALUES ('Tom')"
        )

    def test_insert_5(self):
        self.assertEqual(
            SQLQueryBuilder.insert('users', {'name': 'Tom', 'age': 30, 'region': 'USA'}),
            "INSERT INTO users (name, age, region) VALUES ('Tom', '30', 'USA')"
        )


class SQLQueryBuilderTestDetele(unittest.TestCase):
    def test_delete_1(self):
        self.assertEqual(
            SQLQueryBuilder.delete('users', {'name': 'Tom'}),
            "DELETE FROM users WHERE name='Tom'"
        )

    def test_delete_2(self):
        self.assertEqual(
            SQLQueryBuilder.delete('students', {'name': 'Tom'}),
            "DELETE FROM students WHERE name='Tom'"
        )

    def test_delete_3(self):
        self.assertEqual(
            SQLQueryBuilder.delete('items', {'name': 'apple'}),
            "DELETE FROM items WHERE name='apple'"
        )

    def test_delete_4(self):
        self.assertEqual(
            SQLQueryBuilder.delete('items', {'name': 'aaa'}),
            "DELETE FROM items WHERE name='aaa'"
        )

    def test_delete_5(self):
        self.assertEqual(
            SQLQueryBuilder.delete('items', {'name': 'bbb'}),
            "DELETE FROM items WHERE name='bbb'"
        )

    def test_delete_6(self):
        self.assertEqual(
            SQLQueryBuilder.delete('items'),
            "DELETE FROM items"
        )


class SQLQueryBuilderTestUpdate(unittest.TestCase):
    def test_update_1(self):
        self.assertEqual(
            SQLQueryBuilder.update('users', {'age': 35}, {'name': 'Tom'}),
            "UPDATE users SET age='35' WHERE name='Tom'"
        )

    def test_update_2(self):
        self.assertEqual(
            SQLQueryBuilder.update('students', {'age': 18}, {'name': 'Tom'}),
            "UPDATE students SET age='18' WHERE name='Tom'"
        )

    def test_update_3(self):
        self.assertEqual(
            SQLQueryBuilder.update('items', {'price': 1.0}, {'name': 'apple'}),
            "UPDATE items SET price='1.0' WHERE name='apple'"
        )

    def test_update_4(self):
        self.assertEqual(
            SQLQueryBuilder.update('items', {'price': 1.0}, {'name': 'aaa'}),
            "UPDATE items SET price='1.0' WHERE name='aaa'"
        )

    def test_update_5(self):
        self.assertEqual(
            SQLQueryBuilder.update('items', {'price': 1.0}, {'name': 'bbb'}),
            "UPDATE items SET price='1.0' WHERE name='bbb'"
        )

    def test_update_6(self):
        self.assertEqual(
            SQLQueryBuilder.update('items', {'price': 1.0}),
            "UPDATE items SET price='1.0'"
        )


class SQLQueryBuilderTestMain(unittest.TestCase):
    def test_main(self):
        self.assertEqual(
            SQLQueryBuilder.select('users', ["id", "name"], {'age': 30}),
            "SELECT id, name FROM users WHERE age='30'"
        )
        self.assertEqual(
            SQLQueryBuilder.insert('users', {'name': 'Tom', 'age': 30}),
            "INSERT INTO users (name, age) VALUES ('Tom', '30')"
        )
        self.assertEqual(
            SQLQueryBuilder.delete('users', {'name': 'Tom'}),
            "DELETE FROM users WHERE name='Tom'"
        )
        self.assertEqual(
            SQLQueryBuilder.update('users', {'age': 35}, {'name': 'Tom'}),
            "UPDATE users SET age='35' WHERE name='Tom'"
        )