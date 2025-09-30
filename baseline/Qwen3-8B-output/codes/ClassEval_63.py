import re
from collections import Counter

class NLPDataProcessor2:
    """
    The class processes NLP data by extracting words from a list of strings, calculating the frequency of each word, and returning the top 5 most frequent words.
    """

    def process_data(self, string_list):
        """
        keep only English letters and spaces in the string, then convert the string to lower case, and then split the string into a list of words.
        :param string_list: a list of strings
        :return: words_list: a list of words lists
        >>> NLPDataProcessor2.process_data(['This is a test.'])
        [['this', 'is', 'a', 'test']]
        """
        words_list = []
        for string in string_list:
            cleaned = re.sub(r'[^a-zA-Z\s]', '', string)
            lower_cleaned = cleaned.lower()
            words = lower_cleaned.split()
            words_list.append(words)
        return words_list

    def calculate_word_frequency(self, words_list):
        """
        Calculate the word frequency of each word in the list of words list, and sort the word frequency dictionary by value in descending order.
        :param words_list: a list of words lists
        :return: top 5 word frequency dictionary, a dictionary of word frequency, key is word, value is frequency
        >>> NLPDataProcessor2.calculate_word_frequency([['this', 'is', 'a', 'test'], ['this', 'is', 'another', 'test']])
        {'this': 2, 'is': 2, 'test': 2, 'a': 1, 'another': 1}
        """
        word_counter = Counter()
        for words in words_list:
            word_counter.update(words)
        # Get the top 5 most common words
        top_5 = word_counter.most_common(5)
        # Convert to dictionary
        return dict(top_5)

    def process(self, string_list):
        """
        keep only English letters and spaces in the string, then convert the string to lower case, and then split the string into a list of words. Calculate the word frequency of each word in the list of words list, and sort the word frequency dictionary by value in descending order.
        :param string_list: a list of strings
        :return: top 5 word frequency dictionary, a dictionary of word frequency, key is word, value is frequency
        >>> NLPDataProcessor2.process(['This is a test.', 'This is another test.'])
        {'this': 2, 'is': 2, 'test': 2, 'a': 1, 'another': 1}
        """
        words_list = self.process_data(string_list)
        return self.calculate_word_frequency(words_list)

import unittest

class NLPDataProcessorTestProcessData(unittest.TestCase):

    def setUp(self):
        self.processor = NLPDataProcessor2()

    def test_process_data(self):
        string_list = ["Hello World!", "This is a test."]
        expected_output = [['hello', 'world'], ['this', 'is', 'a', 'test']]
        self.assertEqual(self.processor.process_data(string_list), expected_output)

    def test_process_data2(self):
        string_list = ["12345", "Special@Characters"]
        expected_output = [[], ['specialcharacters']]
        self.assertEqual(self.processor.process_data(string_list), expected_output)

    def test_process_data3(self):
        string_list = []
        expected_output = []
        self.assertEqual(self.processor.process_data(string_list), expected_output)

    def test_process_data4(self):
        string_list = ["Hello World!", "This is a test.", "12345", "Special@Characters"]
        expected_output = [['hello', 'world'], ['this', 'is', 'a', 'test'], [], ['specialcharacters']]
        self.assertEqual(self.processor.process_data(string_list), expected_output)

    def test_process_data5(self):
        string_list = ["Hello World!", "This is a test.", "12345", "Special@Characters", "Hello World!", "This is a test.", "12345", "Special@Characters"]
        expected_output = [['hello', 'world'], ['this', 'is', 'a', 'test'], [], ['specialcharacters'], ['hello', 'world'], ['this', 'is', 'a', 'test'], [], ['specialcharacters']]
        self.assertEqual(self.processor.process_data(string_list), expected_output)

class NLPDataProcessorTestCalculate(unittest.TestCase):

    def setUp(self):
        self.processor = NLPDataProcessor2()

    def test_calculate_word_frequency(self):
        words_list = [['hello', 'world'], ['this', 'is', 'a', 'test'], ['hello', 'world', 'this', 'is', 'another', 'test'],
                      ['hello', 'hello', 'world']]
        expected_output = {'hello': 4, 'world': 3, 'this': 2, 'is': 2, 'test': 2}
        self.assertEqual(self.processor.calculate_word_frequency(words_list), expected_output)

    def test_calculate_word_frequency2(self):
        words_list = [['hello', 'world'], ['this', 'is', 'a', 'test'], ['hello', 'world', 'this', 'is', 'another', 'test'],
                      ['hello', 'hello', 'world'], ['world', 'world', 'world']]
        expected_output = {'world': 6, 'hello': 4, 'this': 2, 'is': 2, 'test': 2}
        self.assertEqual(self.processor.calculate_word_frequency(words_list), expected_output)

    def test_calculate_word_frequency3(self):
        words_list = [['hello', 'world'], ['hello', 'hello', 'world'], ['world', 'world']]
        expected_output = {'world': 4, 'hello': 3}
        self.assertEqual(self.processor.calculate_word_frequency(words_list), expected_output)

    def test_calculate_word_frequency4(self):
        words_list = [['hello', 'world'], ['this', 'is', 'a', '%%%'], ['hello', 'world', 'this', 'is', 'another', '%%%'],
                      ['hello', 'hello', 'world'], ['%%%', 'world', 'a', '%%%'], ['%%%', 'hello', '%%%']]
        expected_output = {'%%%': 6, 'hello': 5, 'world': 4, 'is': 2, 'this': 2}
        self.assertEqual(self.processor.calculate_word_frequency(words_list), expected_output)

    def test_calculate_word_frequency5(self):
        words_list = [['hello', 'world'], ['this', 'is', 'a', '%%%'], ['hello', 'world', 'this', 'is', 'another', '%%%'],
                      ['hello', 'hello', 'world'], ['%%%', 'world', 'a', '%%%'], ['%%%', 'hello', '%%%'], ['hello', 'world'], ['this', 'is', 'a', '%%%'], ['hello', 'world', 'this', 'is', 'another', '%%%'],
                      ['hello', 'hello', 'world'], ['%%%', 'world', 'a', '%%%'], ['%%%', 'hello', '%%%']]
        expected_output = {'%%%': 12, 'hello': 10, 'world': 8, 'is': 4, 'this': 4}
        self.assertEqual(self.processor.calculate_word_frequency(words_list), expected_output)

class NLPDataProcessorTestProcess(unittest.TestCase):

    def setUp(self):
        self.processor = NLPDataProcessor2()

    def test_process(self):
        string_list = ["Hello World!", "This is a test.", "Hello World, this is a test."]
        expected_output = {'hello': 2, 'world': 2, 'this': 2, 'is': 2, 'a': 2}
        self.assertEqual(self.processor.process(string_list), expected_output)

    def test_process2(self):
        string_list = []
        expected_output = []
        self.assertEqual(self.processor.process_data(string_list), expected_output)

    def test_calculate3(self):
        words_list = []
        expected_output = {}
        self.assertEqual(self.processor.calculate_word_frequency(words_list), expected_output)

    def test_process4(self):
        string_list = ["@#$%^&*", "Special_Characters", "12345"]
        expected_output = [[], ['specialcharacters'], []]
        self.assertEqual(self.processor.process_data(string_list), expected_output)

    def test_process5(self):
        string_list = ["Hello World! %%%", "This is a %%% test. %%% ", "Hello World, this is a test. %%%"]
        expected_output = {'hello': 2, 'world': 2, 'this': 2, 'is': 2, 'a': 2}
        self.assertEqual(self.processor.process(string_list), expected_output)

    def test_process6(self):
        string_list = ["12345", "67890", "98765"]
        expected_output = [[], [], []]
        self.assertEqual(self.processor.process_data(string_list), expected_output)