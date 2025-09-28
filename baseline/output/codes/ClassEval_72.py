import re

class RegexUtils:
    """
    The class provides to match, find all occurrences, split, and substitute text using regular expressions. It also includes predefined patterns, validating phone numbers and extracting email addresses.
    """

    def match(self, pattern, text):
        """
        Check if the text matches the regular expression
        :param pattern: string, Regular expression pattern
        :param text: string, Text to match
        :return: True or False, representing whether the text matches the regular expression or not
        >>> ru = RegexUtils()
        >>> ru.match(r'\b\d{3}-\d{3}-\d{4}\b', "123-456-7890")
        True
        """
        return bool(re.fullmatch(pattern, text))
    
    def findall(self, pattern, text):
        """
        Find all matching substrings and return a list of all matching substrings
        :param pattern: string, Regular expression pattern
        :param text: string, Text to match
        :return: list of string, List of all matching substrings
        >>> ru = RegexUtils()
        >>> ru.findall(r'\b\d{3}-\d{3}-\d{4}\b', "123-456-7890 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        ['123-456-7890', '876-286-9876', '987-762-9767']
        """
        return re.findall(pattern, text)
    
    def split(self, pattern, text):
        """
        Split text based on regular expression patterns and return a list of substrings
        :param pattern: string, Regular expression pattern
        :param text: string, Text to be split
        :return: list of string, List of substrings after splitting
        >>> ru = RegexUtils()
        >>> ru.split(r'\b\d{3}-\d{3}-\d{4}\b', "123-456-7890 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        ['', ' abiguygusu ', ' kjgufwycs ', '']
        """
        return re.split(pattern, text)
    
    def sub(self, pattern, replacement, text):
        """
        Replace the substring matched by a regular expression with the specified string
        :param pattern: string, Regular expression pattern
        :param replacement: Text to replace with
        :param text: string, Text to be replaced
        :return: string, Text after replacement
        >>> ru = RegexUtils()
        >>> ru.sub(r'\b\d{3}-\d{3}-\d{4}\b', 'phone num',  "123-456-7890 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        'phone num abiguygusu phone num kjgufwycs phone num'
        """
        return re.sub(pattern, replacement, text)
    
    def generate_email_pattern(self):
        """
        Generate regular expression patterns that match email addresses
        :return: string, regular expression patterns that match email addresses
        >>> ru = RegexUtils()
        >>> ru.generate_email_pattern()
        '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        """
        return r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    def generate_phone_number_pattern(self):
        """
        Generate regular expression patterns that match phone numbers
        :return: string, regular expression patterns that match phone numbers
        >>> ru = RegexUtils()
        >>> ru.generate_phone_number_pattern()
        '\b\d{3}-\d{3}-\d{4}\b'
        """
        return r'\b\d{3}-\d{3}-\d{4}\b'
    
    def generate_split_sentences_pattern(self):
        """
        Generate regular expression patterns that match the middle characters of two sentences
        :return: string, regular expression patterns that match the middle characters of two sentences
        >>> ru = RegexUtils()
        >>> ru.generate_split_sentences_pattern()
        '[.!?][\s]{1,2}(?=[A-Z])'
        """
        return r'[\.\!\?][\s]{1,2}(?=[A-Z])'
    
    def split_sentences(self, text):
        """
        Split the text into a list of sentences without Punctuation except the last sentence
        :param text: Text to be split
        :return: Split Text List
        >>> ru = RegexUtils()
        >>> ru.split_sentences("Aaa. Bbbb? Ccc!")
        ['Aaa', 'Bbbb', 'Ccc!']
        """
        pattern = r'[\.\!\?][\s]{1,2}(?=[A-Z])'
        sentences = re.split(pattern, text)
        if sentences and sentences[-1].endswith('!'):
            sentences[-1] = sentences[-1].rstrip('!') + '!'
        return sentences
    
    def validate_phone_number(self, phone_number):
        """
        Verify if the phone number is valid
        :param phone_number: Phone number to be verified
        :return: True or False, indicating whether the phone number is valid
        >>> ru = RegexUtils()
        >>> ru.validate_phone_number("123-456-7890")
        True
        """
        pattern = r'\b\d{3}-\d{3}-\d{4}\b'
        return bool(re.fullmatch(pattern, phone_number))
    
    def extract_email(self, text):
        """
        Extract all email addresses from the text
        :param text: string, input text
        :return: list of string, All extracted email addresses
        >>> ru = RegexUtils()
        >>> ru.extract_email("abcdefg@163.com ygusyfysy@126.com wljduyuv@qq.com")
        ['abcdefg@163.com', 'ygusyfysy@126.com', 'wljduyuv@qq.com']
        """
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)

import unittest


class RegexUtilsTestMatch(unittest.TestCase):
    def test_match_1(self):
        ru = RegexUtils()
        res = ru.match(r'\b\d{3}-\d{3}-\d{4}\b', "123-456-7890")
        self.assertEqual(res, True)

    def test_match_2(self):
        ru = RegexUtils()
        res = ru.match(r'\b\d{3}-\d{3}-\d{4}\b', "1234567890")
        self.assertEqual(res, False)

    def test_match_3(self):
        ru = RegexUtils()
        res = ru.match(r'\b\d{3}-\d{3}-\d{4}\b', "111-111-1111")
        self.assertEqual(res, True)

    def test_match_4(self):
        ru = RegexUtils()
        res = ru.match(r'\b\d{3}-\d{3}-\d{4}\b', "123-456-789")
        self.assertEqual(res, False)

    def test_match_5(self):
        ru = RegexUtils()
        res = ru.match(r'\b\d{3}-\d{3}-\d{4}\b', "123-456-789a")
        self.assertEqual(res, False)


class RegexUtilsTestFindall(unittest.TestCase):
    def test_findall_1(self):
        ru = RegexUtils()
        res = ru.findall(r'\b\d{3}-\d{3}-\d{4}\b', "123-456-7890 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        self.assertEqual(res, ['123-456-7890', '876-286-9876', '987-762-9767'])

    def test_findall_2(self):
        ru = RegexUtils()
        res = ru.findall(r'\b\d{3}-\d{3}-\d{4}\b', "abiguygusu  kjgufwycs 987-762-9767")
        self.assertEqual(res, ['987-762-9767'])

    def test_findall_3(self):
        ru = RegexUtils()
        res = ru.findall(r'\b\d{3}-\d{3}-\d{4}\b', "abiguygusu  kjgufwycs ")
        self.assertEqual(res, [])

    def test_findall_4(self):
        ru = RegexUtils()
        res = ru.findall(r'\b\d{3}-\d{3}-\d{4}\b', "abiguygusu  111-111-1111 kjgufwycs 987-762-9767")
        self.assertEqual(res, ['111-111-1111', '987-762-9767'])

    def test_findall_5(self):
        ru = RegexUtils()
        res = ru.findall(r'\b\d{3}-\d{3}-\d{4}\b', "abiguygusu  111-111-111a kjgufwycs 987-762-9767")
        self.assertEqual(res, ['987-762-9767'])


class RegexUtilsTestSplit(unittest.TestCase):
    def test_split_1(self):
        ru = RegexUtils()
        res = ru.split(r'\b\d{3}-\d{3}-\d{4}\b', "123-456-7890 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        self.assertEqual(res, ['', ' abiguygusu ', ' kjgufwycs ', ''])

    def test_split_2(self):
        ru = RegexUtils()
        res = ru.split(r'\b\d{3}-\d{3}-\d{4}\b', "1234567890 abiguygusu 8762869876 kjgufwycs 9877629767")
        self.assertEqual(res, ['1234567890 abiguygusu 8762869876 kjgufwycs 9877629767'])

    def test_split_3(self):
        ru = RegexUtils()
        res = ru.split(r'\b\d{3}-\d{3}-\d{4}\b', "111-111-1111 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        self.assertEqual(res, ['', ' abiguygusu ', ' kjgufwycs ', ''])

    def test_split_4(self):
        ru = RegexUtils()
        res = ru.split(r'\b\d{3}-\d{3}-\d{4}\b', "123456-7890 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        self.assertEqual(res, ['123456-7890 abiguygusu ', ' kjgufwycs ', ''])

    def test_split_5(self):
        ru = RegexUtils()
        res = ru.split(r'\b\d{3}-\d{3}-\d{4}\b', "123-456-789a abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        self.assertEqual(res, ['123-456-789a abiguygusu ', ' kjgufwycs ', ''])


class RegexUtilsTestSub(unittest.TestCase):
    def test_sub_1(self):
        ru = RegexUtils()
        res = ru.sub(r'\b\d{3}-\d{3}-\d{4}\b', 'phone num',
                     "123-456-7890 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        self.assertEqual(res, 'phone num abiguygusu phone num kjgufwycs phone num')

    def test_sub_2(self):
        ru = RegexUtils()
        res = ru.sub(r'\b\d{3}-\d{3}-\d{4}\b', 'phone num',
                     "1234567890 abiguygusu 8762869876 kjgufwycs 9877629767")
        self.assertEqual(res, "1234567890 abiguygusu 8762869876 kjgufwycs 9877629767")

    def test_sub_3(self):
        ru = RegexUtils()
        res = ru.sub(r'\b\d{3}-\d{3}-\d{4}\b', 'phone num',
                     "123456-7890 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        self.assertEqual(res, '123456-7890 abiguygusu phone num kjgufwycs phone num')

    def test_sub_4(self):
        ru = RegexUtils()
        res = ru.sub(r'\b\d{3}-\d{3}-\d{4}\b', 'phone num',
                     "123-456-789a abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        self.assertEqual(res, '123-456-789a abiguygusu phone num kjgufwycs phone num')

    def test_sub_5(self):
        ru = RegexUtils()
        res = ru.sub(r'\b\d{3}-\d{3}-\d{4}\b', 'phone num',
                     "123-456-780 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        self.assertEqual(res, '123-456-780 abiguygusu phone num kjgufwycs phone num')


class RegexUtilsTestGenerateEmailPattern(unittest.TestCase):
    def test_generate_email_pattern_1(self):
        ru = RegexUtils()
        pat = ru.generate_email_pattern()
        res = ru.match(pat, 'iustd87t2euh@163.com')
        self.assertEqual(res, True)

    def test_generate_email_pattern_2(self):
        ru = RegexUtils()
        pat = ru.generate_email_pattern()
        res = ru.match(pat, 'iustd87t2euhifg.com')
        self.assertEqual(res, False)

    def test_generate_email_pattern_3(self):
        ru = RegexUtils()
        pat = ru.generate_email_pattern()
        res = ru.match(pat, 'iustd87t2euhifg@.com')
        self.assertEqual(res, False)

    def test_generate_email_pattern_4(self):
        ru = RegexUtils()
        pat = ru.generate_email_pattern()
        res = ru.match(pat, 'iustd87t2euhifg@.')
        self.assertEqual(res, False)

    def test_generate_email_pattern_5(self):
        ru = RegexUtils()
        pat = ru.generate_email_pattern()
        res = ru.match(pat, 'iustd87t2euhifg@com.')
        self.assertEqual(res, False)


class RegexUtilsTestGeneratePhoneNumberPattern(unittest.TestCase):
    def test_generate_phone_number_pattern_1(self):
        ru = RegexUtils()
        pat = ru.generate_phone_number_pattern()
        res = ru.match(pat, '123-456-7890')
        self.assertEqual(res, True)

    def test_generate_phone_number_pattern_2(self):
        ru = RegexUtils()
        pat = ru.generate_phone_number_pattern()
        res = ru.match(pat, '1234567890')
        self.assertEqual(res, False)

    def test_generate_phone_number_pattern_3(self):
        ru = RegexUtils()
        pat = ru.generate_phone_number_pattern()
        res = ru.match(pat, '123-456-789')
        self.assertEqual(res, False)

    def test_generate_phone_number_pattern_4(self):
        ru = RegexUtils()
        pat = ru.generate_phone_number_pattern()
        res = ru.match(pat, 'a23-456-7890')
        self.assertEqual(res, False)

    def test_generate_phone_number_pattern_5(self):
        ru = RegexUtils()
        pat = ru.generate_phone_number_pattern()
        res = ru.match(pat, '1234-56-7890')
        self.assertEqual(res, False)


class RegexUtilsTestGenerateSplitSentencesPattern(unittest.TestCase):
    def test_generate_split_sentences_pattern_1(self):
        ru = RegexUtils()
        pat = ru.generate_split_sentences_pattern()
        res = ru.match(pat, '? Y')
        self.assertEqual(res, True)

    def test_generate_split_sentences_pattern_2(self):
        ru = RegexUtils()
        pat = ru.generate_split_sentences_pattern()
        res = ru.match(pat, '! Y')
        self.assertEqual(res, True)

    def test_generate_split_sentences_pattern_3(self):
        ru = RegexUtils()
        pat = ru.generate_split_sentences_pattern()
        res = ru.match(pat, '? ')
        self.assertEqual(res, False)

    def test_generate_split_sentences_pattern_4(self):
        ru = RegexUtils()
        pat = ru.generate_split_sentences_pattern()
        res = ru.match(pat, '?Y')
        self.assertEqual(res, False)

    def test_generate_split_sentences_pattern_5(self):
        ru = RegexUtils()
        pat = ru.generate_split_sentences_pattern()
        res = ru.match(pat, '.Y')
        self.assertEqual(res, False)


class RegexUtilsTestSplitSentences(unittest.TestCase):
    def test_split_sentences_1(self):
        ru = RegexUtils()
        res = ru.split_sentences("Aaa. Bbbb? Ccc!")
        self.assertEqual(res, ['Aaa', 'Bbbb', 'Ccc!'])

    def test_split_sentences_2(self):
        ru = RegexUtils()
        res = ru.split_sentences("Aaa.Bbbb? Ccc!")
        self.assertEqual(res, ['Aaa.Bbbb', 'Ccc!'])

    def test_split_sentences_3(self):
        ru = RegexUtils()
        res = ru.split_sentences("Aaa. bbbb? Ccc!")
        self.assertEqual(res, ['Aaa. bbbb', 'Ccc!'])

    def test_split_sentences_4(self):
        ru = RegexUtils()
        res = ru.split_sentences("Aaa. bbbb, Ccc!")
        self.assertEqual(res, ['Aaa. bbbb, Ccc!'])

    def test_split_sentences_5(self):
        ru = RegexUtils()
        res = ru.split_sentences("Aaa, Bbbb? Ccc!")
        self.assertEqual(res, ['Aaa, Bbbb', 'Ccc!'])


class RegexUtilsTestValidatePhoneNumber(unittest.TestCase):
    def test_validate_phone_number_1(self):
        ru = RegexUtils()
        res = ru.validate_phone_number("123-456-7890")
        self.assertEqual(res, True)

    def test_validate_phone_number_2(self):
        ru = RegexUtils()
        res = ru.validate_phone_number("1234567890")
        self.assertEqual(res, False)

    def test_validate_phone_number_3(self):
        ru = RegexUtils()
        res = ru.validate_phone_number("a23-456-7890")
        self.assertEqual(res, False)

    def test_validate_phone_number_4(self):
        ru = RegexUtils()
        res = ru.validate_phone_number("123-456-789")
        self.assertEqual(res, False)

    def test_validate_phone_number_5(self):
        ru = RegexUtils()
        res = ru.validate_phone_number("1234-56-789")
        self.assertEqual(res, False)


class RegexUtilsTestExtractEmail(unittest.TestCase):
    def test_extract_email_1(self):
        ru = RegexUtils()
        res = ru.extract_email("abcdefg@163.com ygusyfysy@126.com wljduyuv@qq.com")
        self.assertEqual(res, ['abcdefg@163.com', 'ygusyfysy@126.com', 'wljduyuv@qq.com'])

    def test_extract_email_2(self):
        ru = RegexUtils()
        res = ru.extract_email("abcdefg@.com ygusyfysy@126.com wljduyuv@qq.com")
        self.assertEqual(res, ['ygusyfysy@126.com', 'wljduyuv@qq.com'])

    def test_extract_email_3(self):
        ru = RegexUtils()
        res = ru.extract_email("abcdefgiscom ygusyfysy@126.com wljduyuv@qq.com")
        self.assertEqual(res, ['ygusyfysy@126.com', 'wljduyuv@qq.com'])

    def test_extract_email_4(self):
        ru = RegexUtils()
        res = ru.extract_email("abcdefgiscom ygusyfysy126.com wljduyuv@qq.com")
        self.assertEqual(res, ['wljduyuv@qq.com'])

    def test_extract_email_5(self):
        ru = RegexUtils()
        res = ru.extract_email("abcdefgiscom ygusyfysy@.com wljduyuv@qq.com")
        self.assertEqual(res, ['wljduyuv@qq.com'])


class RegexUtilsTest(unittest.TestCase):
    def test_regexutils(self):
        ru = RegexUtils()
        res = ru.match(r'\b\d{3}-\d{3}-\d{4}\b', "123-456-7890")
        self.assertEqual(res, True)

        res = ru.findall(r'\b\d{3}-\d{3}-\d{4}\b', "123-456-7890 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        self.assertEqual(res, ['123-456-7890', '876-286-9876', '987-762-9767'])

        res = ru.split(r'\b\d{3}-\d{3}-\d{4}\b', "123-456-7890 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        self.assertEqual(res, ['', ' abiguygusu ', ' kjgufwycs ', ''])

        res = ru.sub(r'\b\d{3}-\d{3}-\d{4}\b', 'phone num',
                     "123-456-7890 abiguygusu 876-286-9876 kjgufwycs 987-762-9767")
        self.assertEqual(res, 'phone num abiguygusu phone num kjgufwycs phone num')

        pat = ru.generate_email_pattern()
        res = ru.match(pat, 'iustd87t2euh@163.com')
        self.assertEqual(res, True)

        pat = ru.generate_phone_number_pattern()
        res = ru.match(pat, '123-456-7890')
        self.assertEqual(res, True)

        pat = ru.generate_split_sentences_pattern()
        res = ru.match(pat, '? Y')
        self.assertEqual(res, True)

        res = ru.split_sentences("Aaa. Bbbb? Ccc!")
        self.assertEqual(res, ['Aaa', 'Bbbb', 'Ccc!'])

        res = ru.validate_phone_number("123-456-7890")
        self.assertEqual(res, True)

        res = ru.extract_email("abcdefg@163.com ygusyfysy@126.com wljduyuv@qq.com")
        self.assertEqual(res, ['abcdefg@163.com', 'ygusyfysy@126.com', 'wljduyuv@qq.com'])