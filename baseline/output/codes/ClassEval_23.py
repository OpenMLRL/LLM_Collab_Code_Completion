import math
from typing import List

class CombinationCalculator:
    """
    This is a class that provides methods to calculate the number of combinations for a specific count, calculate all possible combinations, and generate combinations with a specified number of elements.
    """

    def __init__(self, datas: List[str]):
        """
        Initialize the calculator with a list of data.
        """
        self.datas = datas

    @staticmethod
    def count(n: int, m: int) -> int:
        """
        Calculate the number of combinations for a specific count.
        :param n: The total number of elements,int.
        :param m: The number of elements in each combination,int.
        :return: The number of combinations,int.
        >>> CombinationCalculator.count(4, 2)
        6
        """
        return math.factorial(n) // (math.factorial(m) * math.factorial(n - m))

    @staticmethod
    def count_all(n: int) -> int:
        """
        Calculate the number of all possible combinations.
        :param n: The total number of elements,int.
        :return: The number of all possible combinations,int,if the number of combinations is greater than 2^63-1,return float("inf").
        >>> CombinationCalculator.count_all(4)
        15
        """
        return math.factorial(n)

    def select(self, m: int) -> List[List[str]]:
        """
        Generate combinations with a specified number of elements.
        :param m: The number of elements in each combination,int.
        :return: A list of combinations,List[List[str]].
        >>> calc = CombinationCalculator(["A", "B", "C", "D"])
        >>> calc.select(2)
        [['A', 'B'], ['A', 'C'], ['A', 'D'], ['B', 'C'], ['B', 'D'], ['C', 'D']]
        """
        if m > len(self.datas):
            return []
        if m == 0:
            return [[]]
        if m == 1:
            return [[data] for data in self.datas]
        result = []
        for i in range(len(self.datas) - m + 1):
            for sub_combination in self.select(m - 1):
                result.append([self.datas[i]] + sub_combination)
        return result

    def select_all(self) -> List[List[str]]:
        """
        Generate all possible combinations of selecting elements from the given data list, and it uses the select method.
        :return: A list of combinations,List[List[str]].
        >>> calc = CombinationCalculator(["A", "B", "C", "D"])
        >>> calc.select_all()
        [['A'], ['B'], ['C'], ['D'], ['A', 'B'], ['A', 'C'], ['A', 'D'], ['B', 'C'], ['B', 'D'], ['C', 'D'], ['A', 'B', 'C'], ['A', 'B', 'D'], ['A', 'C', 'D'], ['B', 'C', 'D'], ['A', 'B', 'C', 'D']]
        """
        return self.select(len(self.datas))

    def _select(self, dataIndex: int, resultList: List[str], resultIndex: int, result: List[List[str]]):
        """
        Generate combinations with a specified number of elements by recursion.
        :param dataIndex: The index of the data to be selected,int.
        :param resultList: The list of elements in the combination,List[str].
        :param resultIndex: The index of the element in the combination,int.
        :param result: The list of combinations,List[List[str]].
        :return: None.
        >>> calc = CombinationCalculator(["A", "B", "C", "D"])
        >>> result = []
        >>> calc._select(0, [None] * 2, 0, result)
        >>> result
        [['A', 'B'], ['A', 'C'], ['A', 'D'], ['B', 'C'], ['B', 'D'], ['C', 'D']]
        """
        if resultIndex == len(resultList):
            result.append(resultList[:])
            return
        for i in range(dataIndex, len(self.datas)):
            resultList[resultIndex] = self.datas[i]
            self._select(i + 1, resultList, resultIndex + 1, result)

import unittest

class CombinationCalculatorTestCount(unittest.TestCase):
    def test_count(self):
        self.assertEqual(CombinationCalculator.count(4, 2), 6)
    def test_count_2(self):
        self.assertEqual(CombinationCalculator.count(5, 3), 10)

    def test_count_3(self):
        self.assertEqual(CombinationCalculator.count(6, 6), 1)

    def test_count_4(self):
        self.assertEqual(CombinationCalculator.count(6, 0), 1)

    def test_count_5(self):
        self.assertEqual(CombinationCalculator.count(6, 3), 20)

class CombinationCalculatorTestCountAll(unittest.TestCase):
    def test_count_all(self):
        self.assertEqual(CombinationCalculator.count_all(4), 15)

    def test_count_all_2(self):
        self.assertEqual(CombinationCalculator.count_all(-1), False)

    def test_count_all_3(self):
        self.assertEqual(CombinationCalculator.count_all(65), False)

    def test_count_all_4(self):
        self.assertEqual(CombinationCalculator.count_all(0), 0)

    def test_count_all_5(self):
        self.assertEqual(CombinationCalculator.count_all(63), float("inf"))

class CombinationCalculatorTestSelect(unittest.TestCase):
    def test_select(self):
        calc = CombinationCalculator(["A", "B", "C", "D"])
        self.assertEqual(calc.count(4, 2), 6)

    def test_select_2(self):
        calc = CombinationCalculator(["A", "B", "C", "D"])
        self.assertEqual(calc.count(5, 3), 10)

    def test_select_3(self):
        calc = CombinationCalculator(["A", "B", "C", "D"])
        self.assertEqual(calc.count(6, 6), 1)

    def test_select_4(self):
        calc = CombinationCalculator(["A", "B", "C", "D"])
        self.assertEqual(calc.count(6, 0), 1)

    def test_select_5(self):
        calc = CombinationCalculator(["A", "B", "C", "D"])
        self.assertEqual(calc.count(6, 3), 20)

class CombinationCalculatorTestSelectAll(unittest.TestCase):
    def test_select_all(self):
        calc = CombinationCalculator(["A"])
        self.assertEqual(calc.select_all(), [['A']])

    def test_select_all_2(self):
        calc = CombinationCalculator(["A", "B"])
        self.assertEqual(calc.select_all(), [['A'], ['B'], ['A', 'B']])

    def test_select_all_3(self):
        calc = CombinationCalculator(["A", "B", "C"])
        self.assertEqual(calc.select_all(),[['A'], ['B'], ['C'], ['A', 'B'], ['A', 'C'], ['B', 'C'], ['A', 'B', 'C']])

    def test_select_all_4(self):
        calc = CombinationCalculator([])
        self.assertEqual(calc.select_all(),[])

    def test_select_all_5(self):
        calc = CombinationCalculator(["B"])
        self.assertEqual(calc.select_all(),[['B']])


class CombinationCalculatorTestSelect2(unittest.TestCase):
    def test_select2(self):
        calc = CombinationCalculator(["A", "B", "C", "D"])
        result = []
        calc._select(0, [None] * 2, 0, result)
        self.assertEqual(result, [['A', 'B'], ['A', 'C'], ['A', 'D'], ['B', 'C'], ['B', 'D'], ['C', 'D']])

    def test_select2_2(self):
        calc = CombinationCalculator(["A", "B", "C", "D"])
        result = []
        calc._select(0, [None] * 3, 0, result)
        self.assertEqual(result, [['A', 'B', 'C'], ['A', 'B', 'D'], ['A', 'C', 'D'], ['B', 'C', 'D']])

    def test_select2_3(self):
        calc = CombinationCalculator(["A", "B", "C", "D"])
        result = []
        calc._select(0, [None] * 1, 0, result)
        self.assertEqual(result, [['A'], ['B'], ['C'], ['D']])

    def test_select2_4(self):
        calc = CombinationCalculator(["A", "B", "C", "D"])
        result = []
        calc._select(0, [None] * 0, 0, result)
        self.assertEqual(result, [[]])

    def test_select2_5(self):
        calc = CombinationCalculator(["A", "B", "C", "D"])
        result = []
        calc._select(0, [None] * 4, 0, result)
        self.assertEqual(result, [['A', 'B', 'C', 'D']])

class CombinationCalculatorTestMain(unittest.TestCase):
    def test_main(self):
        calc = CombinationCalculator(["A", "B", "C", "D"])
        self.assertEqual(calc.count(4, 2), 6)
        self.assertEqual(calc.count_all(4), 15)
        self.assertEqual(calc.select(2), [['A', 'B'], ['A', 'C'], ['A', 'D'], ['B', 'C'], ['B', 'D'], ['C', 'D']])
        self.assertEqual(calc.select_all(), [['A'], ['B'], ['C'], ['D'], ['A', 'B'], ['A', 'C'], ['A', 'D'], ['B', 'C'], ['B', 'D'], ['C', 'D'], ['A', 'B', 'C'], ['A', 'B', 'D'], ['A', 'C', 'D'], ['B', 'C', 'D'], ['A', 'B', 'C', 'D']])
        result = []
        calc._select(0, [None] * 2, 0, result)
        self.assertEqual(result, [['A', 'B'], ['A', 'C'], ['A', 'D'], ['B', 'C'], ['B', 'D'], ['C', 'D']])