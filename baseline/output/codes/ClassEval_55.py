class Manacher:
    """
    this is a class that implements a manacher algorithm to find the Longest palindromic substring in a given string.
    """

    def __init__(self, input_string) -> None:
        """
        Initializes the Manacher class with the given input_string.
        :param input_string: The input_string to be searched, str.
        """
        self.input_string = input_string

    def palindromic_length(self, center, diff, string):
        """
        Recursively calculates the length of the palindromic substring based on a given center, difference value, and input string.
        :param center: The center of the palindromic substring, int.
        :param diff: The difference between the center and the current position, int.
        :param string: The string to be searched, str.
        :return: The length of the palindromic substring, int.
        >>> manacher = Manacher('ababa')
        >>> manacher.palindromic_length(2, 1, 'a|b|a|b|a')
        2
        """
        if center + diff >= len(string) or center - diff < 0:
            return 0
        if string[center + diff] != string[center - diff]:
            return 0
        return 2 * diff + 1

    def palindromic_string(self):
        """
        Finds the longest palindromic substring in the given string.
        :return: The longest palindromic substring, str.
        >>> manacher = Manacher('ababaxse')
        >>> manacher.palindromic_string()
        'ababa'
        """
        if not self.input_string:
            return ""
        # Preprocess the string to handle even and odd length palindromes
        processed = '#' + '#'.join(self.input_string) + '#'
        n = len(processed)
        p = [0] * n  # Array to store the length of palindrome centered at each index
        center, right = 0, 0
        max_len = 0
        center_index = 0

        for i in range(n):
            # Find the mirror of i
            mirror = 2 * center - i
            # Check if i is within the right boundary
            if i < right:
                p[i] = min(right - i, p[mirror])
            # Attempt to expand palindrome centered at i
            a = i + p[i] + 1
            b = i - p[i] - 1
            while 0 <= a < n and 0 <= b < n and processed[a] == processed[b]:
                p[i] += 1
                a += 1
                b -= 1
            # Update the center and right boundary if needed
            if i + p[i] > right:
                center = i
                right = i + p[i]
            # Update the maximum length and its center index
            if p[i] > max_len:
                max_len = p[i]
                center_index = i
        # Extract the longest palindromic substring from the processed string
        start = (center_index - max_len) // 2
        end = start + max_len
        return self.input_string[start:end]

import unittest

class ManacherTestPalindromicLength(unittest.TestCase):
    def test_palindromic_length(self):
        manacher = Manacher('ababa')
        self.assertEqual(manacher.palindromic_length(2, 1, 'a|b|a|b|a'), 2)
    def test_palindromic_length_2(self):
        manacher = Manacher('ababaxse')
        self.assertEqual(manacher.palindromic_length(2, 1, 'a|b|a|b|a|x|s|e'), 2)

    def test_palindromic_length_3(self):
        manacher = Manacher('ababax')
        self.assertEqual(manacher.palindromic_length(2, 3, 'a|b|a|b|a|x'), 0)

    def test_palindromic_length_4(self):
        manacher = Manacher('ababax')
        self.assertEqual(manacher.palindromic_length(9, 2, 'a|b|a|b|a|x'), 0)

    def test_palindromic_length_5(self):
        manacher = Manacher('ababax')
        self.assertEqual(manacher.palindromic_length(4, 1, 'a|b|a|b|a|x'), 4)


class ManacherTestPalindromicString(unittest.TestCase):
    def test_palindromic_string(self):
        manacher = Manacher('ababaxse')
        self.assertEqual(manacher.palindromic_string(), 'ababa')

    def test_palindromic_string_2(self):
        manacher = Manacher('ababax')
        self.assertEqual(manacher.palindromic_string(), 'ababa')

    def test_palindromic_string_3(self):
        manacher = Manacher('ababax')
        self.assertEqual(manacher.palindromic_string(), 'ababa')

    def test_palindromic_string_4(self):
        manacher = Manacher('ababaxssss')
        self.assertEqual(manacher.palindromic_string(), 'ababa')

    def test_palindromic_string_5(self):
        manacher = Manacher('abab')
        self.assertEqual(manacher.palindromic_string(), 'aba')


class ManacherTestMain(unittest.TestCase):
    def test_main(self):
        manacher = Manacher('ababa')
        self.assertEqual(manacher.palindromic_length(2, 1, 'a|b|a|b|a'), 2)
        self.assertEqual(manacher.palindromic_string(), 'ababa')