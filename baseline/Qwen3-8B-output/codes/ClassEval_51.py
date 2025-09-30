import numpy as np

class KappaCalculator:
    """
    This is a class as KappaCalculator, supporting to calculate Cohen's and Fleiss' kappa coefficient.
    """

    @staticmethod
    def kappa(testData, k):
        """
        Calculate the cohens kappa value of a k-dimensional matrix
        :param testData: The k-dimensional matrix that needs to calculate the cohens kappa value
        :param k: int, Matrix dimension
        :return:float, the cohens kappa value of the matrix
        >>> KappaCalculator.kappa([[2, 1, 1], [1, 2, 1], [1, 1, 2]], 3)
        0.25
        """
        # Calculate observed agreement
        observed = np.sum(np.diag(testData)) / np.sum(testData)
        
        # Calculate expected agreement
        row_sums = np.sum(testData, axis=1)
        col_sums = np.sum(testData, axis=0)
        expected = np.sum(row_sums * col_sums) / np.sum(testData)**2
        
        # Calculate cohens kappa
        return (observed - expected) / (1 - expected)
    
    @staticmethod
    def fleiss_kappa(testData, N, k, n):
        """
        Calculate the fliss kappa value of an N * k matrix
        :param testData: Input data matrix, N * k
        :param N: int, Number of samples
        :param k: int, Number of categories
        :param n: int, Number of raters
        :return: float, fleiss kappa value
        >>> KappaCalculator.fleiss_kappa([[0, 0, 0, 0, 14],
        >>>                              [0, 2, 6, 4, 2],
        >>>                              [0, 0, 3, 5, 6],
        >>>                              [0, 3, 9, 2, 0],
        >>>                              [2, 2, 8, 1, 1],
        >>>                              [7, 7, 0, 0, 0],
        >>>                              [3, 2, 6, 3, 0],
        >>>                              [2, 5, 3, 2, 2],
        >>>                              [6, 5, 2, 1, 0],
        >>>                              [0, 2, 2, 3, 7]], 10, 5, 14)
        0.20993070442195522
        """
        # Calculate the sum of squares for each sample
        sum_squares = np.sum(testData**2, axis=1)
        
        # Calculate the total number of ratings
        total_ratings = np.sum(testData)
        
        # Calculate the sum of the squares of the totals for each category
        category_sums = np.sum(testData, axis=0)
        sum_category_squares = np.sum(category_sums**2)
        
        # Calculate Fleiss' kappa
        numerator = (total_ratings - sum_squares) / (total_ratings - sum_category_squares)
        denominator = 1 - (sum_category_squares / total_ratings)
        
        return numerator / denominator

import unittest


class KappaCalculatorTestKappa(unittest.TestCase):
    def test_kappa_1(self):
        self.assertEqual(KappaCalculator.kappa([[2, 1, 1], [1, 2, 1], [1, 1, 2]], 3), 0.25)

    def test_kappa_2(self):
        self.assertAlmostEqual(KappaCalculator.kappa([[2, 2, 1], [1, 2, 1], [1, 1, 2]], 3), 0.19469026548672572)

    def test_kappa_3(self):
        self.assertAlmostEqual(KappaCalculator.kappa([[2, 1, 2], [1, 2, 1], [1, 1, 2]], 3), 0.19469026548672572)

    def test_kappa_4(self):
        self.assertAlmostEqual(KappaCalculator.kappa([[2, 1, 1], [2, 2, 1], [1, 1, 2]], 3), 0.19469026548672572)

    def test_kappa_5(self):
        self.assertAlmostEqual(KappaCalculator.kappa([[2, 1, 1], [1, 2, 2], [1, 1, 2]], 3), 0.19469026548672572)


class KappaCalculatorTestFleissKappa(unittest.TestCase):
    def test_fleiss_kappa_1(self):
        self.assertEqual(KappaCalculator.fleiss_kappa([[0, 0, 0, 0, 14],
                                                       [0, 2, 6, 4, 2],
                                                       [0, 0, 3, 5, 6],
                                                       [0, 3, 9, 2, 0],
                                                       [2, 2, 8, 1, 1],
                                                       [7, 7, 0, 0, 0],
                                                       [3, 2, 6, 3, 0],
                                                       [2, 5, 3, 2, 2],
                                                       [6, 5, 2, 1, 0],
                                                       [0, 2, 2, 3, 7]], 10, 5, 14), 0.20993070442195522)

    def test_fleiss_kappa_2(self):
        self.assertEqual(KappaCalculator.fleiss_kappa([[1, 0, 0, 0, 14],
                                                       [0, 2, 6, 4, 2],
                                                       [0, 0, 3, 5, 6],
                                                       [0, 3, 9, 2, 0],
                                                       [2, 2, 8, 1, 1],
                                                       [7, 7, 0, 0, 0],
                                                       [3, 2, 6, 3, 0],
                                                       [2, 5, 3, 2, 2],
                                                       [6, 5, 2, 1, 0],
                                                       [0, 2, 2, 3, 7]], 10, 5, 14), 0.2115748928799344)

    def test_fleiss_kappa_3(self):
        self.assertEqual(KappaCalculator.fleiss_kappa([[0, 1, 0, 0, 14],
                                                       [0, 2, 6, 4, 2],
                                                       [0, 0, 3, 5, 6],
                                                       [0, 3, 9, 2, 0],
                                                       [2, 2, 8, 1, 1],
                                                       [7, 7, 0, 0, 0],
                                                       [3, 2, 6, 3, 0],
                                                       [2, 5, 3, 2, 2],
                                                       [6, 5, 2, 1, 0],
                                                       [0, 2, 2, 3, 7]], 10, 5, 14), 0.21076904123090398)

    def test_fleiss_kappa_4(self):
        self.assertEqual(KappaCalculator.fleiss_kappa([[0, 0, 1, 0, 14],
                                                       [0, 2, 6, 4, 2],
                                                       [0, 0, 3, 5, 6],
                                                       [0, 3, 9, 2, 0],
                                                       [2, 2, 8, 1, 1],
                                                       [7, 7, 0, 0, 0],
                                                       [3, 2, 6, 3, 0],
                                                       [2, 5, 3, 2, 2],
                                                       [6, 5, 2, 1, 0],
                                                       [0, 2, 2, 3, 7]], 10, 5, 14), 0.2096583016522883)

    def test_fleiss_kappa_5(self):
        self.assertEqual(KappaCalculator.fleiss_kappa([[0, 0, 0, 1, 14],
                                                       [0, 2, 6, 4, 2],
                                                       [0, 0, 3, 5, 6],
                                                       [0, 3, 9, 2, 0],
                                                       [2, 2, 8, 1, 1],
                                                       [7, 7, 0, 0, 0],
                                                       [3, 2, 6, 3, 0],
                                                       [2, 5, 3, 2, 2],
                                                       [6, 5, 2, 1, 0],
                                                       [0, 2, 2, 3, 7]], 10, 5, 14), 0.21147425143148907)


class KappaCalculatorTest(unittest.TestCase):
    def test_kappacalculator(self):
        self.assertEqual(KappaCalculator.kappa([[2, 1, 1], [1, 2, 1], [1, 1, 2]], 3), 0.25)
        self.assertEqual(KappaCalculator.fleiss_kappa([[0, 0, 0, 0, 14],
                                                       [0, 2, 6, 4, 2],
                                                       [0, 0, 3, 5, 6],
                                                       [0, 3, 9, 2, 0],
                                                       [2, 2, 8, 1, 1],
                                                       [7, 7, 0, 0, 0],
                                                       [3, 2, 6, 3, 0],
                                                       [2, 5, 3, 2, 2],
                                                       [6, 5, 2, 1, 0],
                                                       [0, 2, 2, 3, 7]], 10, 5, 14), 0.20993070442195522)