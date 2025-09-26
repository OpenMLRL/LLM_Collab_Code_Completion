import sqlite3

class BookManagementDB:
    """
    This is a database class as a book management system, used to handle the operations of adding, removing, updating, and searching books.
    """

    def __init__(self, db_name):
        """
        Initializes the class by creating a database connection and cursor, 
        and creates the book table if it does not already exist
        :param db_name: str, the name of db file
        """
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        """
        Creates the book table in the database if it does not already exist.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT,
                author TEXT,
                availability INTEGER
            )
        ''')
        self.connection.commit()

    def add_book(self, title, author):
        """
        Adds a book to the database with the specified title and author, 
        setting its availability to 1 as free to borrow.
        :param title: str, book title
        :param author: str, author name
        """
        self.cursor.execute('''
            INSERT INTO books (title, author, availability) VALUES (?, ?, ?)
        ''', (title, author, 1))
        self.connection.commit()

    def remove_book(self, book_id):
        """
        Removes a book from the database based on the given book ID.
        :param book_id: int
        """
        self.cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
        self.connection.commit()

    def borrow_book(self, book_id):
        """
        Marks a book as borrowed in the database based on the given book ID.
        :param book_id: int
        """
        self.cursor.execute('UPDATE books SET availability = 0 WHERE id = ?', (book_id,))
        self.connection.commit()

    def return_book(self, book_id):
        """
        Marks a book as returned in the database based on the given book ID.
        :param book_id: int
        """
        self.cursor.execute('UPDATE books SET availability = 1 WHERE id = ?', (book_id,))
        self.connection.commit()

    def search_books(self):
        """
        Retrieves all books from the database and returns their information.
        :return books: list[tuple], the information of all books in database
        """
        self.cursor.execute('SELECT * FROM books')
        return self.cursor.fetchall()

import unittest
import os


class BookManagementDBTestCreateTable(unittest.TestCase):
    def setUp(self):
        self.db_name = "test.db"
        self.db = BookManagementDB(self.db_name)
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def test_create_table_1(self):
        # Check if the table exists
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)

    def test_create_table_2(self):
        self.db.create_table()
        # Check if the table has the correct columns
        self.cursor.execute("PRAGMA table_info(books)")
        columns = self.cursor.fetchall()
        column_names = [column[1] for column in columns]
        expected_column_names = ['id', 'title', 'author', 'available']
        self.assertEqual(column_names, expected_column_names)

    def tearDown(self):
        self.db.connection.close()
        self.connection.close()
        # remove the test database file
        os.remove(self.db_name)


class BookManagementDBTestAddBook(unittest.TestCase):
    def setUp(self):
        self.db_name = "test.db"
        self.db = BookManagementDB(self.db_name)
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def test_add_book(self):
        title = "Introduction to Python"
        author = "John Smith"
        self.db.add_book(title, author)

        # Check if the book was added correctly
        self.cursor.execute("SELECT title, author, available FROM books WHERE id=1")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], title)
        self.assertEqual(result[1], author)
        self.assertEqual(result[2], 1)

    def tearDown(self):
        self.db.connection.close()
        self.connection.close()
        # remove the test database file
        os.remove(self.db_name)


class BookManagementDBTestRemoveBook(unittest.TestCase):
    def setUp(self):
        self.db_name = "test.db"
        self.db = BookManagementDB(self.db_name)
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        # Add a book for testing removal
        self.db.add_book("Book to Remove", "John Doe")

    def test_remove_book(self):
        self.db.remove_book(1)

        # Check if the book was removed correctly
        self.cursor.execute("SELECT * FROM books WHERE id=1")
        result = self.cursor.fetchone()
        self.assertIsNone(result)

    def tearDown(self):
        self.db.connection.close()
        self.connection.close()
        # remove the test database file
        os.remove(self.db_name)


class BookManagementDBTestBorrowBook(unittest.TestCase):
    def setUp(self):
        self.db_name = "test.db"
        self.db = BookManagementDB(self.db_name)
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        # Add a book for testing borrowing
        self.db.add_book("Book to Borrow", "Jane Smith")

    def test_borrow_book(self):
        self.db.borrow_book(1)

        # Check if the book was marked as unavailable
        self.cursor.execute("SELECT available FROM books WHERE id=1")
        result = self.cursor.fetchone()
        self.assertEqual(result[0], 0)

    def tearDown(self):
        self.db.connection.close()
        self.connection.close()
        # remove the test database file
        os.remove(self.db_name)


class BookManagementDBTestReturnBook(unittest.TestCase):
    def setUp(self):
        self.db_name = "test.db"
        self.db = BookManagementDB(self.db_name)
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        # Add a book for testing returning
        self.db.add_book("Book to Return", "James Smith")
        self.db.borrow_book(1)  # Mark the book as borrowed

    def test_return_book(self):
        self.db.return_book(1)

        # Check if the book was marked as available again
        self.cursor.execute("SELECT available FROM books WHERE id=1")
        result = self.cursor.fetchone()
        self.assertEqual(result[0], 1)

    def tearDown(self):
        self.db.connection.close()
        self.connection.close()
        # remove the test database file
        os.remove(self.db_name)


class BookManagementDBTestSearchBooks(unittest.TestCase):
    def setUp(self):
        self.db_name = "test.db"
        self.db = BookManagementDB(self.db_name)
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        # Add some books for testing search
        self.db.add_book("Book 1", "Author 1")
        self.db.add_book("Book 2", "Author 2")
        self.db.add_book("Book 3", "Author 3")

    def test_search_books(self):
        books = self.db.search_books()

        # Ensure that all books were retrieved
        self.assertEqual(len(books), 3)

        # Ensure that the correct book information is retrieved
        self.assertEqual(books[0][1], "Book 1")
        self.assertEqual(books[1][2], "Author 2")
        self.assertEqual(books[2][3], 1)

    def tearDown(self):
        self.db.connection.close()
        self.connection.close()
        # remove the test database file
        os.remove(self.db_name)