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