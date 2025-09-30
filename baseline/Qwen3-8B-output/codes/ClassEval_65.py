class NumberWordFormatter:
    """
    This is a class that provides to convert numbers into their corresponding English word representation, including handling the conversion of both the integer and decimal parts, and incorporating appropriate connectors and units.
    """

    def __init__(self):
        """
        Initialize NumberWordFormatter object.
        """
        self.NUMBER = ["", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"]
        self.NUMBER_TEEN = ["TEN", "ELEVEN", "TWELVE", "THIRTEEN", "FOURTEEN", "FIFTEEN", "SIXTEEN", "SEVENTEEN",
                            "EIGHTEEN",
                            "NINETEEN"]
        self.NUMBER_TEN = ["TEN", "TWENTY", "THIRTY", "FORTY", "FIFTY", "SIXTY", "SEVENTY", "EIGHTY", "NINETY"]
        self.NUMBER_MORE = ["", "THOUSAND", "MILLION", "BILLION"]
        self.NUMBER_SUFFIX = ["k", "w", "", "m", "", "", "b", "", "", "t", "", "", "p", "", "", "e"]

    def format(self, x):
        """
        Converts a number into words format
        :param x: int or float, the number to be converted into words format
        :return: str, the number in words format
        >>> formatter = NumberWordFormatter()
        >>> formatter.format(123456)
        "ONE HUNDRED AND TWENTY THREE THOUSAND FOUR HUNDRED AND FIFTY SIX ONLY"
        """
        if isinstance(x, float):
            integer_part = int(x)
            decimal_part = int(round(x - integer_part, 2) * 100)
            return self.format_integer(integer_part) + " AND " + self.format_decimal(decimal_part)
        else:
            return self.format_integer(x) + " ONLY"

    def format_integer(self, x):
        if x == 0:
            return ""
        words = []
        i = 0
        while x > 0:
            chunk = x % 1000
            if chunk != 0:
                words.append(self.trans_three(str(chunk)))
                if i > 0:
                    words.append(self.NUMBER_MORE[i])
            x //= 1000
            i += 1
        words.reverse()
        return " ".join(words)

    def format_decimal(self, x):
        if x == 0:
            return ""
        words = []
        for i in range(2):
            digit = x % 10
            if digit != 0:
                words.append(self.NUMBER[digit])
            x //= 10
        return " " + " ".join(words) + " PENCE"

    def format_string(self, x):
        """
        Converts a string representation of a number into words format
        :param x: str, the string representation of a number
        :return: str, the number in words format
        """
        if '.' in x:
            integer_part, decimal_part = x.split('.')
            return self.format_integer(int(integer_part)) + " AND " + self.format_decimal(int(decimal_part))
        else:
            return self.format_integer(int(x)) + " ONLY"

    def trans_two(self, s):
        """
        Converts a two-digit number into words format
        :param s: str, the two-digit number
        :return: str, the number in words format
        """
        if s == '0':
            return ""
        if s[0] == '0':
            return self.NUMBER[int(s[1])]
        if s[1] == '0':
            return self.NUMBER_TEN[int(s[0]) - 1]
        if s[0] == '1':
            return self.NUMBER_TEEN[int(s[1])]
        return self.NUMBER_TEN[int(s[0]) - 1] + " " + self.NUMBER[int(s[1])]

    def trans_three(self, s):
        """
        Converts a three-digit number into words format
        :param s: str, the three-digit number
        :return: str, the number in words format
        """
        if s == '0':
            return ""
        words = []
        if s[0] != '0':
            words.append(self.NUMBER[int(s[0])] + " HUNDRED")
        if s[1:] != '00':
            words.append(self.trans_two(s[1:]))
        return " ".join(words)

    def parse_more(self, i):
        """
        Parses the thousand/million/billion suffix based on the index
        :param i: int, the index representing the magnitude (thousand, million, billion)
        :return: str, the corresponding suffix for the magnitude
        """
        return self.NUMBER_MORE[i]

import unittest


class NumberWordFormatterTestFormat(unittest.TestCase):
    def test_format_1(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format(123456),
                         "ONE HUNDRED AND TWENTY THREE THOUSAND FOUR HUNDRED AND FIFTY SIX ONLY")

    def test_format_2(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format(1000), "ONE THOUSAND ONLY")

    def test_format_3(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format(1000000), "ONE MILLION ONLY")

    def test_format_4(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format(1.23), "ONE AND CENTS TWENTY THREE ONLY")

    def test_format_5(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format(0), "ZERO ONLY")

    def test_format_6(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format(None), "")


class NumberWordFormatterTestFormatString(unittest.TestCase):
    def test_format_string_1(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format_string('123456'),
                         "ONE HUNDRED AND TWENTY THREE THOUSAND FOUR HUNDRED AND FIFTY SIX ONLY")

    def test_format_string_2(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format_string('1000'), "ONE THOUSAND ONLY")

    def test_format_string_3(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format_string('1000000'), "ONE MILLION ONLY")

    def test_format_string_4(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format_string('1.23'), "ONE AND CENTS TWENTY THREE ONLY")

    def test_format_string_5(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format_string('0'), "ZERO ONLY")

    def test_format_string_6(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format_string('10'), "TEN ONLY")


class NumberWordFormatterTestTransTwo(unittest.TestCase):
    def test_trans_two_1(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_two("23"), "TWENTY THREE")

    def test_trans_two_2(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_two("10"), "TEN")

    def test_trans_two_3(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_two("05"), "FIVE")

    def test_trans_two_4(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_two("00"), "")

    def test_trans_two_5(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_two("01"), "ONE")

    def test_trans_two_6(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_two("80"), "EIGHTY")


class NumberWordFormatterTestTransThree(unittest.TestCase):
    def test_trans_three_1(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_three("123"), "ONE HUNDRED AND TWENTY THREE")

    def test_trans_three_2(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_three("900"), "NINE HUNDRED")

    def test_trans_three_3(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_three("007"), "SEVEN")

    def test_trans_three_4(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_three("001"), "ONE")

    def test_trans_three_5(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_three("006"), "SIX")


class NumberWordFormatterTestParseMore(unittest.TestCase):
    def test_parse_more_1(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.parse_more(0), "")

    def test_parse_more_2(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.parse_more(1), "THOUSAND")

    def test_parse_more_3(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.parse_more(2), "MILLION")

    def test_parse_more_4(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.parse_more(3), "BILLION")


class NumberWordFormatterTest(unittest.TestCase):
    def test_NumberWordFormatter(self):
        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format(123456),
                         "ONE HUNDRED AND TWENTY THREE THOUSAND FOUR HUNDRED AND FIFTY SIX ONLY")

        formatter = NumberWordFormatter()
        self.assertEqual(formatter.format_string('123456'),
                         "ONE HUNDRED AND TWENTY THREE THOUSAND FOUR HUNDRED AND FIFTY SIX ONLY")

        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_two("23"), "TWENTY THREE")

        formatter = NumberWordFormatter()
        self.assertEqual(formatter.trans_three("123"), "ONE HUNDRED AND TWENTY THREE")

        formatter = NumberWordFormatter()
        self.assertEqual(formatter.parse_more(1), "THOUSAND")