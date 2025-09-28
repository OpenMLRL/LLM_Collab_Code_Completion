import json

class TextFileProcessor:
    """
    The class handles reading, writing, and processing text files. It can read the file as JSON, read the raw text, write content to the file, and process the file by removing non-alphabetic characters.
    """

    def __init__(self, file_path):
        """
        Initialize the file path.
        :param file_path: str
        """
        self.file_path = file_path

    def read_file_as_json(self):
        """
        Read the self.file_path file as json format.
        if the file content doesn't obey json format, the code will raise error.
        :return data: dict if the file is stored as json format, or str/int/float.. according to the file content otherwise.
        >>> textFileProcessor = TextFileProcessor('test.json')
        >>> textFileProcessor.read_file_as_json()
        {'name': 'test', 'age': 12}
        >>> type(textFileProcessor.read_file_as_json())
        <class 'dict'>
        """
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def read_file(self):
        """
        Read the return the content of self.file_path file.
        :return: the same return as the read() method
        >>> textFileProcessor = TextFileProcessor('test.json')
        >>> textFileProcessor.read_file()
        '{\n    "name": "test",\n    "age": 12\n}'
        """
        with open(self.file_path, 'r') as file:
            return file.read()

    def write_file(self, content):
        """
        Write content into the self.file_path file, and overwrite if the file has already existed.
        :param content: any content
        >>> textFileProcessor = TextFileProcessor('test.json')
        >>> textFileProcessor.write_file('Hello world!')
        >>> textFileProcessor.read_file()
        'Hello world!'
        """
        with open(self.file_path, 'w') as file:
            file.write(str(content))

    def process_file(self):
        """
        Read the self.file_path file and filter out non-alphabetic characters from the content string.
        Overwrite the after-processed data into the same self.file_path file.
        >>> textFileProcessor = TextFileProcessor('test.json')
        >>> textFileProcessor.read_file()
        '{\n    "name": "test",\n    "age": 12\n}'
        >>> textFileProcessor.process_file()
        'nametestage'
        """
        content = self.read_file()
        processed = ''.join(char for char in content if char.isalpha())
        self.write_file(processed)
        return processed

import unittest
import json
from unittest.mock import MagicMock
import os


class TextFileProcessorTestReadFileAsJson(unittest.TestCase):
    def setUp(self):
        self.files = ['test_1.txt', 'test_2.txt', 'test_3.txt', 'test_4.txt', 'test_5.txt']
        self.contents = ['{\n    "name": "test",\n    "age": 12\n}', '12345', '\"hello\"', '\"aaa\"', '\"bbb\"']
        for index, file in enumerate(self.files):
            with open(file, 'w') as f:
                f.write(self.contents[index])

    # the dict type
    def test_read_file_as_json_1(self):
        textFileProcessor = TextFileProcessor(self.files[0])
        data = textFileProcessor.read_file_as_json()
        expected = {"name": "test", "age": 12}
        self.assertEqual(dict, type(data))
        self.assertEqual(expected, data)

    # the int type
    def test_read_file_as_json_2(self):
        textFileProcessor = TextFileProcessor(self.files[1])
        data = textFileProcessor.read_file_as_json()
        expected = 12345
        self.assertEqual(int, type(data))
        self.assertEqual(expected, data)

    # the str type
    def test_read_file_as_json_3(self):
        textFileProcessor = TextFileProcessor(self.files[2])
        data = textFileProcessor.read_file_as_json()
        expected = 'hello'
        self.assertEqual(str, type(data))
        self.assertEqual(expected, data)

    def test_read_file_as_json_4(self):
        textFileProcessor = TextFileProcessor(self.files[3])
        data = textFileProcessor.read_file_as_json()
        expected = 'aaa'
        self.assertEqual(str, type(data))
        self.assertEqual(expected, data)

    def test_read_file_as_json_5(self):
        textFileProcessor = TextFileProcessor(self.files[4])
        data = textFileProcessor.read_file_as_json()
        expected = 'bbb'
        self.assertEqual(str, type(data))
        self.assertEqual(expected, data)


class TextFileProcessorTestReadFile(unittest.TestCase):
    def setUp(self) -> None:
        self.files = ['test_1.txt', 'test_2.txt', 'test_3.txt', 'test_4.txt', 'test_5.txt']
        self.contents = ['123aac\n&^(*&43)', '12345', 'aaa', 'bbb', 'ccc']
        for index, file in enumerate(self.files):
            with open(file, 'w') as f:
                f.write(self.contents[index])

    def test_read_file_1(self):
        textFileProcessor = TextFileProcessor(self.files[0])
        data = textFileProcessor.read_file()
        self.assertEqual(str, type(data))
        self.assertEqual(data, self.contents[0])

    def test_read_file_2(self):
        textFileProcessor = TextFileProcessor(self.files[1])
        data = textFileProcessor.read_file()
        self.assertEqual(str, type(data))
        self.assertEqual(data, self.contents[1])

    def test_read_file_3(self):
        textFileProcessor = TextFileProcessor(self.files[2])
        data = textFileProcessor.read_file()
        self.assertEqual(str, type(data))
        self.assertEqual(data, self.contents[2])

    def test_read_file_4(self):
        textFileProcessor = TextFileProcessor(self.files[3])
        data = textFileProcessor.read_file()
        self.assertEqual(str, type(data))
        self.assertEqual(data, self.contents[3])

    def test_read_file_5(self):
        textFileProcessor = TextFileProcessor(self.files[4])
        data = textFileProcessor.read_file()
        self.assertEqual(str, type(data))
        self.assertEqual(data, self.contents[4])


class TextFileProcessorTestWriteFile(unittest.TestCase):
    def setUp(self) -> None:
        self.files = ['test_1.txt', 'test_2.txt', 'test_3.txt', 'test_4.txt', 'test_5.txt']
        self.contents = ['123aac\n&^(*&43)', '12345', 'aaa', 'bbb', 'ccc']

    def tearDown(self) -> None:
        for file in self.files:
            if os.path.exists(file):
                os.remove(file)

    def test_write_file_1(self):
        textFileProcessor = TextFileProcessor(self.files[0])
        textFileProcessor.write_file(self.contents[0])
        with open(self.files[0], 'r') as f:
            data = f.read()
        self.assertEqual(data, self.contents[0])

    def test_write_file_2(self):
        textFileProcessor = TextFileProcessor(self.files[1])
        textFileProcessor.write_file(self.contents[1])
        with open(self.files[1], 'r') as f:
            data = f.read()
        self.assertEqual(data, self.contents[1])

    def test_write_file_3(self):
        textFileProcessor = TextFileProcessor(self.files[2])
        textFileProcessor.write_file(self.contents[2])
        with open(self.files[2], 'r') as f:
            data = f.read()
        self.assertEqual(data, self.contents[2])

    def test_write_file_4(self):
        textFileProcessor = TextFileProcessor(self.files[3])
        textFileProcessor.write_file(self.contents[3])
        with open(self.files[3], 'r') as f:
            data = f.read()
        self.assertEqual(data, self.contents[3])

    def test_write_file_5(self):
        textFileProcessor = TextFileProcessor(self.files[4])
        textFileProcessor.write_file(self.contents[4])
        with open(self.files[4], 'r') as f:
            data = f.read()
        self.assertEqual(data, self.contents[4])


class TextFileProcessorTestProcessFile(unittest.TestCase):
    def test_process_file_1(self):
        self.file = 'test.txt'
        self.content = 'Hello, 123 World!'
        self.expected_result = 'HelloWorld'

        textFileProcessor = TextFileProcessor(self.file)
        textFileProcessor.read_file = MagicMock(return_value=self.content)
        textFileProcessor.write_file = MagicMock()

        result = textFileProcessor.process_file()
        self.assertEqual(result, self.expected_result)
        textFileProcessor.read_file.assert_called_once()
        textFileProcessor.write_file.assert_called_once_with(self.expected_result)

    def test_process_file_2(self):
        self.file = 'test.txt'
        self.content = 'Hello, abc World!'
        self.expected_result = 'HelloabcWorld'

        textFileProcessor = TextFileProcessor(self.file)
        textFileProcessor.read_file = MagicMock(return_value=self.content)
        textFileProcessor.write_file = MagicMock()

        result = textFileProcessor.process_file()
        self.assertEqual(result, self.expected_result)
        textFileProcessor.read_file.assert_called_once()
        textFileProcessor.write_file.assert_called_once_with(self.expected_result)

    def test_process_file_3(self):
        self.file = 'test.txt'
        self.content = ', 123 !'
        self.expected_result = ''

        textFileProcessor = TextFileProcessor(self.file)
        textFileProcessor.read_file = MagicMock(return_value=self.content)
        textFileProcessor.write_file = MagicMock()

        result = textFileProcessor.process_file()
        self.assertEqual(result, self.expected_result)
        textFileProcessor.read_file.assert_called_once()
        textFileProcessor.write_file.assert_called_once_with(self.expected_result)

    def test_process_file_4(self):
        self.file = 'test.txt'
        self.content = 'Hello, World!'
        self.expected_result = 'HelloWorld'

        textFileProcessor = TextFileProcessor(self.file)
        textFileProcessor.read_file = MagicMock(return_value=self.content)
        textFileProcessor.write_file = MagicMock()

        result = textFileProcessor.process_file()
        self.assertEqual(result, self.expected_result)
        textFileProcessor.read_file.assert_called_once()
        textFileProcessor.write_file.assert_called_once_with(self.expected_result)

    def test_process_file_5(self):
        self.file = 'test.txt'
        self.content = 'Hello, 123a World!'
        self.expected_result = 'HelloaWorld'

        textFileProcessor = TextFileProcessor(self.file)
        textFileProcessor.read_file = MagicMock(return_value=self.content)
        textFileProcessor.write_file = MagicMock()

        result = textFileProcessor.process_file()
        self.assertEqual(result, self.expected_result)
        textFileProcessor.read_file.assert_called_once()
        textFileProcessor.write_file.assert_called_once_with(self.expected_result)


class TextFileProcessorTestMain(unittest.TestCase):
    def setUp(self) -> None:
        self.file = 'test.txt'
        self.content = '{\n    "name": "test",\n    "age": 12\n}'
        with open(self.file, 'w') as f:
            f.write(self.content)

    def test_main(self):
        textFileProcessor = TextFileProcessor(self.file)
        data1 = textFileProcessor.read_file_as_json()
        expected1 = {"name": "test", "age": 12}
        self.assertEqual(dict, type(data1))
        self.assertEqual(expected1, data1)

        textFileProcessor.write_file(self.content)
        data2 = textFileProcessor.read_file()
        self.assertEqual(str, type(data2))
        self.assertEqual(self.content, data2)

        data3 = textFileProcessor.process_file()
        self.assertEqual(str, type(data3))
        expected2 = 'nametestage'
        self.assertEqual(expected2, data3)