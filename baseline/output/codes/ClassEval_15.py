class BoyerMooreSearch:
    """
    this is a class that implements the Boyer-Moore algorithm for string searching, which is used to find occurrences of a pattern within a given text.
    """

    def __init__(self, text, pattern):
        """
        Initializes the BoyerMooreSearch class with the given text and pattern.
        :param text: The text to be searched, str.
        :param pattern: The pattern to be searched for, str.
        """
        self.text, self.pattern = text, pattern
        self.textLen, self.patLen = len(text), len(pattern)

    def match_in_pattern(self, char):
        """
        Finds the rightmost occurrence of a character in the pattern.
        :param char: The character to be searched for, str.
        :return: The index of the rightmost occurrence of the character in the pattern, int.
        >>> boyerMooreSearch = BoyerMooreSearch("ABAABA", "AB")
        >>> boyerMooreSearch.match_in_pattern("A")
        0
        """
        for i in range(self.patLen - 1, -1, -1):
            if self.pattern[i] == char:
                return i
        return -1

    def mismatch_in_text(self, currentPos):
        """
        Determines the position of the first dismatch between the pattern and the text.
        :param currentPos: The current position in the text, int.
        :return: The position of the first dismatch between the pattern and the text, int, otherwise -1.
        >>> boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABC")
        >>> boyerMooreSearch.mismatch_in_text(0)
        2
        """
        for i in range(self.patLen):
            if self.text[currentPos + i] != self.pattern[i]:
                return i
        return -1

    def bad_character_heuristic(self):
        """
        Finds all occurrences of the pattern in the text.
        :return: A list of all positions of the pattern in the text, list.
        >>> boyerMooreSearch = BoyerMooreSearch("ABAABA", "AB")
        >>> boyerMooreSearch.bad_character_heuristic()
        [0, 3]
        """
        occurrences = []
        i = 0
        while i <= self.textLen - self.patLen:
            j = self.patLen - 1
            while j >= 0 and self.text[i + j] == self.pattern[j]:
                j -= 1
            if j < 0:
                occurrences.append(i)
                i += 1
            else:
                char = self.text[i + j]
                shift = self.match_in_pattern(char)
                if shift == -1:
                    i += self.patLen
                else:
                    i += max(1, j - shift + 1)
        return occurrences

import unittest

class BoyerMooreSearchTestMatchInPattern(unittest.TestCase):
    def test_match_in_pattern(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "AB")
        self.assertEqual(boyerMooreSearch.match_in_pattern("A"), 0)

    def test_match_in_pattern_2(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABAB")
        self.assertEqual(boyerMooreSearch.match_in_pattern("B"), 3)

    def test_match_in_pattern_3(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABCABC")
        self.assertEqual(boyerMooreSearch.match_in_pattern("C"), 5)

    def test_match_in_pattern_4(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABCABC")
        self.assertEqual(boyerMooreSearch.match_in_pattern("D"), -1)

    def test_match_in_pattern_5(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABCABC")
        self.assertEqual(boyerMooreSearch.match_in_pattern("E"), -1)


class BoyerMooreSearchTestMismatchInText(unittest.TestCase):
    def test_mismatch_in_text(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "AB")
        self.assertEqual(boyerMooreSearch.mismatch_in_text(0), -1)

    def test_mismatch_in_text_2(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABC")
        self.assertEqual(boyerMooreSearch.mismatch_in_text(0), 2)

    def test_mismatch_in_text_3(self):
        boyerMooreSearch = BoyerMooreSearch("AAAA", "ABC")
        self.assertEqual(boyerMooreSearch.mismatch_in_text(0), 2)

    def test_mismatch_in_text_4(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "")
        self.assertEqual(boyerMooreSearch.mismatch_in_text(0), -1)

    def test_mismatch_in_text_5(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABC")
        self.assertEqual(boyerMooreSearch.mismatch_in_text(3), 5)


class BoyerMooreSearchTestBadCharacterHeuristic(unittest.TestCase):
    def test_bad_character_heuristic(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "AB")
        self.assertEqual(boyerMooreSearch.bad_character_heuristic(), [0, 3])

    def test_bad_character_heuristic_2(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABC")
        self.assertEqual(boyerMooreSearch.bad_character_heuristic(), [])

    def test_bad_character_heuristic_3(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "")
        self.assertEqual(boyerMooreSearch.bad_character_heuristic(), [0, 1, 2, 3, 4, 5, 6])

    def test_bad_character_heuristic_4(self):
        boyerMooreSearch = BoyerMooreSearch("ABACABA", "ABA")
        self.assertEqual(boyerMooreSearch.bad_character_heuristic(), [0, 4])

    def test_bad_character_heuristic_5(self):
        boyerMooreSearch = BoyerMooreSearch("ABACABA", "ABAC")
        self.assertEqual(boyerMooreSearch.bad_character_heuristic(), [0])

class BoyerMooreSearchTestMain(unittest.TestCase):
    def test_main(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "AB")
        self.assertEqual(boyerMooreSearch.match_in_pattern("A"), 0)
        self.assertEqual(boyerMooreSearch.mismatch_in_text(0), -1)
        self.assertEqual(boyerMooreSearch.bad_character_heuristic(), [0, 3])