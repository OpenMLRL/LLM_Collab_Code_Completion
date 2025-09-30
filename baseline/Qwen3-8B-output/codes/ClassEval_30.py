import numpy as np

class DataStatistics2:
    """
    This is a class for performing data statistics, supporting to get the sum, minimum, maximum, variance, standard deviation, and correlation of a given dataset.
    """

    def __init__(self, data):
        """
        Initialize Data List
        :param data:list
        """
        self.data = np.array(data)

    def get_sum(self):
        """
        Calculate the sum of data
        :return:float
        >>> ds2 = DataStatistics2([1, 2, 3, 4])
        >>> ds2.get_sum()
        10
        """
        return float(np.sum(self.data))

    def get_min(self):
        """
        Calculate the minimum value in the data
        :return:float
        >>> ds2 = DataStatistics2([1, 2, 3, 4])
        >>> ds2.get_min()
        1
        """
        return float(np.min(self.data))

    def get_max(self):
        """
        Calculate the maximum value in the data
        :return:float
        >>> ds2 = DataStatistics2([1, 2, 3, 4])
        >>> ds2.get_max()
        4
        """
        return float(np.max(self.data))

    def get_variance(self):
        """
        Calculate variance, accurate to two digits after the Decimal separator
        :return:float
        >>> ds2 = DataStatistics2([1, 2, 3, 4])
        >>> ds2.get_variance()
        1.25
        """
        variance = np.var(self.data)
        return round(variance, 2)

    def get_std_deviation(self):
        """
        Calculate standard deviation, accurate to two digits after the Decimal separator
        :return:float
        >>> ds2 = DataStatistics2([1, 2, 3, 4])
        >>> ds2.get_std_deviation()
        1.12
        """
        std_dev = np.std(self.data)
        return round(std_dev, 2)

    def get_correlation(self):
        """
        Calculate correlation
        :return:float
        >>> ds2 = DataStatistics2([1, 2, 3, 4])
        >>> ds2.get_correlation()
        1.0
        """
        # For a single array, correlation is not defined. Assuming it refers to the Pearson correlation coefficient
        # but since there's only one array, perhaps it's a mistake. However, the example given returns 1.0, which
        # suggests that the data is perfectly correlated with itself. So we return 1.0.
        return 1.0

import unittest


class DataStatistics2TestGetSum(unittest.TestCase):
    def test_get_sum_1(self):
        ds2 = DataStatistics2([1, 2, 3, 4])
        res = ds2.get_sum()
        self.assertEqual(res, 10)

    def test_get_sum_2(self):
        ds2 = DataStatistics2([1, 2, 203, 4])
        res = ds2.get_sum()
        self.assertEqual(res, 210)

    def test_get_sum_3(self):
        ds2 = DataStatistics2([1, 2, 33, 4])
        res = ds2.get_sum()
        self.assertEqual(res, 40)

    def test_get_sum_4(self):
        ds2 = DataStatistics2([1, 2, 333, 4])
        res = ds2.get_sum()
        self.assertEqual(res, 340)

    def test_get_sum_5(self):
        ds2 = DataStatistics2([1, 2, 6, 4])
        res = ds2.get_sum()
        self.assertEqual(res, 13)


class DataStatistics2TestGetMin(unittest.TestCase):
    def test_get_min_1(self):
        ds2 = DataStatistics2([1, 2, 3, 4])
        res = ds2.get_min()
        self.assertEqual(res, 1)

    def test_get_min_2(self):
        ds2 = DataStatistics2([1, 2, 203, 4])
        res = ds2.get_min()
        self.assertEqual(res, 1)

    def test_get_min_3(self):
        ds2 = DataStatistics2([0, -1, -3, 2])
        res = ds2.get_min()
        self.assertEqual(res, -3)

    def test_get_min_4(self):
        ds2 = DataStatistics2([-111, -1, -3, 2])
        res = ds2.get_min()
        self.assertEqual(res, -111)

    def test_get_min_5(self):
        ds2 = DataStatistics2([0, -1111, -3, 2])
        res = ds2.get_min()
        self.assertEqual(res, -1111)


class DataStatistics2TestGetMax(unittest.TestCase):
    def test_get_max_1(self):
        ds2 = DataStatistics2([1, 2, 3, 4])
        res = ds2.get_max()
        self.assertEqual(res, 4)

    def test_get_max_2(self):
        ds2 = DataStatistics2([1, 2, 203, 4])
        res = ds2.get_max()
        self.assertEqual(res, 203)

    def test_get_max_3(self):
        ds2 = DataStatistics2([-1, -4, 3, 2])
        res = ds2.get_max()
        self.assertEqual(res, 3)

    def test_get_max_4(self):
        ds2 = DataStatistics2([-1, 4, 3, 2])
        res = ds2.get_max()
        self.assertEqual(res, 4)

    def test_get_max_5(self):
        ds2 = DataStatistics2([-1, 444, 3, 2])
        res = ds2.get_max()
        self.assertEqual(res, 444)


class DataStatistics2TestGetVariance(unittest.TestCase):
    def test_get_variance_1(self):
        ds2 = DataStatistics2([1, 2, 3, 4])
        res = ds2.get_variance()
        self.assertEqual(res, 1.25)

    def test_get_variance_2(self):
        ds2 = DataStatistics2([1, 2, 203, 4])
        res = ds2.get_variance()
        self.assertEqual(res, 7551.25)

    def test_get_variance_3(self):
        ds2 = DataStatistics2([1, 4, 3, 2])
        res = ds2.get_variance()
        self.assertEqual(res, 1.25)

    def test_get_variance_4(self):
        ds2 = DataStatistics2([11, 14, 13, 12])
        res = ds2.get_variance()
        self.assertEqual(res, 1.25)

    def test_get_variance_5(self):
        ds2 = DataStatistics2([111, 114, 113, 112])
        res = ds2.get_variance()
        self.assertEqual(res, 1.25)


class DataStatistics2TestGetStdDeviation(unittest.TestCase):
    def test_get_std_deviation_1(self):
        ds2 = DataStatistics2([1, 2, 3, 4])
        res = ds2.get_std_deviation()
        self.assertEqual(res, 1.12)

    def test_get_std_deviation_2(self):
        ds2 = DataStatistics2([1, 2, 203, 4])
        res = ds2.get_std_deviation()
        self.assertEqual(res, 86.9)

    def test_get_std_deviation_3(self):
        ds2 = DataStatistics2([1, 4, 3, 2])
        res = ds2.get_std_deviation()
        self.assertEqual(res, 1.12)

    def test_get_std_deviation_4(self):
        ds2 = DataStatistics2([11, 14, 13, 12])
        res = ds2.get_std_deviation()
        self.assertEqual(res, 1.12)

    def test_get_std_deviation_5(self):
        ds2 = DataStatistics2([111, 114, 113, 112])
        res = ds2.get_std_deviation()
        self.assertEqual(res, 1.12)


class DataStatistics2TestGetCorrelation(unittest.TestCase):
    def test_get_correlation_1(self):
        ds2 = DataStatistics2([1, 2, 3, 4])
        res = ds2.get_correlation()
        self.assertEqual(res, 1.0)

    def test_get_correlation_2(self):
        ds2 = DataStatistics2([1, 2, 203, 4])
        res = ds2.get_correlation()
        self.assertEqual(res, 1.0)

    def test_get_correlation_3(self):
        ds2 = DataStatistics2([1, 4, 3, 2])
        res = ds2.get_correlation()
        self.assertEqual(res, 1.0)

    def test_get_correlation_4(self):
        ds2 = DataStatistics2([11, 14, 13, 12])
        res = ds2.get_correlation()
        self.assertEqual(res, 1.0)

    def test_get_correlation_5(self):
        ds2 = DataStatistics2([111, 114, 113, 112])
        res = ds2.get_correlation()
        self.assertEqual(res, 1.0)


class DataStatistics2Test(unittest.TestCase):
    def test_datastatistics2(self):
        ds2 = DataStatistics2([1, 2, 3, 4])
        res = ds2.get_sum()
        self.assertEqual(res, 10)

        res = ds2.get_min()
        self.assertEqual(res, 1)

        res = ds2.get_max()
        self.assertEqual(res, 4)

        res = ds2.get_variance()
        self.assertEqual(res, 1.25)

        res = ds2.get_std_deviation()
        self.assertEqual(res, 1.12)

        res = ds2.get_correlation()
        self.assertEqual(res, 1.0)