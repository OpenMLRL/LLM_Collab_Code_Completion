import math

class DataStatistics4:
    """
    This is a class that performs advanced mathematical calculations and statistics, including correlation coefficient, skewness, kurtosis, and probability density function (PDF) for a normal distribution.
    """

    @staticmethod
    def correlation_coefficient(data1, data2):
        """
        Calculate the correlation coefficient of two sets of data.
        :param data1: The first set of data,list.
        :param data2: The second set of data,list.
        :return: The correlation coefficient, float.
        >>> DataStatistics4.correlation_coefficient([1, 2, 3], [4, 5, 6])
        0.9999999999999998
        """
        n = len(data1)
        mean1 = sum(data1) / n
        mean2 = sum(data2) / n
        covariance = sum((data1[i] - mean1) * (data2[i] - mean2) for i in range(n)) / (n - 1)
        std1 = math.sqrt(sum((data1[i] - mean1) ** 2 for i in range(n)) / (n - 1))
        std2 = math.sqrt(sum((data2[i] - mean2) ** 2 for i in range(n)) / (n - 1))
        return covariance / (std1 * std2)

    @staticmethod
    def skewness(data):
        """
        Calculate the skewness of a set of data.
        :param data: The input data list, list.
        :return: The skewness, float.
        >>> DataStatistics4.skewness([1, 2, 5])
        2.3760224064818463
        """
        n = len(data)
        mean = sum(data) / n
        std = math.sqrt(sum((x - mean) ** 2 for x in data) / (n - 1))
        return sum((x - mean) ** 3 for x in data) / (std ** 3 * (n - 1))

    @staticmethod
    def kurtosis(data):
        """
        Calculate the kurtosis of a set of data.
        :param data: The input data list, list.
        :return: The kurtosis, float.
        >>> DataStatistics4.kurtosis([1, 20,100])
        -1.5000000000000007
        """
        n = len(data)
        mean = sum(data) / n
        std = math.sqrt(sum((x - mean) ** 2 for x in data) / (n - 1))
        return sum((x - mean) ** 4 for x in data) / (std ** 4 * (n - 1)) - 3

    @staticmethod
    def pdf(data, mu, sigma):
        """
        Calculate the probability density function (PDF) of a set of data under a normal distribution.
        :param data: The input data list, list.
        :param mu: The mean of the normal distribution, float.
        :param sigma: The standard deviation of the normal distribution, float.
        :return: The probability density function (PDF), list.
        >>> DataStatistics4.pdf([1, 2, 3], 1, 1)
        [0.3989422804014327, 0.24197072451914337, 0.05399096651318806]
        """
        return [(1 / (sigma * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x - mu) / sigma) ** 2) for x in data]

import unittest


class DataStatistics4TestCorrelationCoefficient(unittest.TestCase):
    def test_correlation_coefficient(self):
        self.assertEqual(DataStatistics4.correlation_coefficient([1, 2, 3], [4, 5, 6]), 0.9999999999999998)

    def test_correlation_coefficient_2(self):
        self.assertEqual(DataStatistics4.correlation_coefficient([1, 1, 1], [2, 2, 2]), 0)

    def test_correlation_coefficient_3(self):
        self.assertEqual(DataStatistics4.correlation_coefficient([1, 2, 3], [1, 2, 3]), 0.9999999999999998)

    def test_correlation_coefficient_4(self):
        self.assertEqual(DataStatistics4.correlation_coefficient([1, 2, 3], [1, 2, 4]), 0.9819805060619659)

    def test_correlation_coefficient_5(self):
        self.assertEqual(DataStatistics4.correlation_coefficient([1, 2, 3], [1, 5, 3]), 0.4999999999999999)


class DataStatistics4TestSkewness(unittest.TestCase):
    def test_skewness(self):
        self.assertEqual(DataStatistics4.skewness([1, 2, 5]), 2.3760224064818463)

    def test_skewness_2(self):
        self.assertEqual(DataStatistics4.skewness([1, 1, 1]), 0)

    def test_skewness_3(self):
        self.assertEqual(DataStatistics4.skewness([1, 2, 3]), 0)

    def test_skewness_4(self):
        self.assertEqual(DataStatistics4.skewness([1, 2, 4]), 1.7181079837227264)

    def test_skewness_5(self):
        self.assertEqual(DataStatistics4.skewness([1, 5, 3]), 0.0)


class DataStatistics4TestKurtosis(unittest.TestCase):
    def test_kurtosis(self):
        self.assertEqual(DataStatistics4.kurtosis([1, 2, 5]), -1.5000000000000002)

    def test_kurtosis_2(self):
        self.assertTrue(math.isnan(DataStatistics4.kurtosis([1, 1, 1])))

    def test_kurtosis_3(self):
        self.assertEqual(DataStatistics4.kurtosis([1, 2, 3]), -1.5000000000000002)

    def test_kurtosis_4(self):
        self.assertEqual(DataStatistics4.kurtosis([1, 2, 4]), -1.4999999999999996)

    def test_kurtosis_5(self):
        self.assertEqual(DataStatistics4.kurtosis([1, 5, 3]), -1.5000000000000002)


class DataStatistics4TestPDF(unittest.TestCase):
    def test_pdf(self):
        self.assertEqual(DataStatistics4.pdf([1, 2, 3], 1, 1),
                         [0.3989422804014327, 0.24197072451914337, 0.05399096651318806])

    def test_pdf_2(self):
        self.assertEqual(DataStatistics4.pdf([1, 1, 1], 1, 1),
                         [0.3989422804014327, 0.3989422804014327, 0.3989422804014327])

    def test_pdf_3(self):
        self.assertEqual(DataStatistics4.pdf([1, 2, 3], 2, 1),
                         [0.24197072451914337, 0.3989422804014327, 0.24197072451914337])

    def test_pdf_4(self):
        self.assertEqual(DataStatistics4.pdf([1, 2, 3], 1, 2),
                         [0.19947114020071635, 0.17603266338214976, 0.12098536225957168])

    def test_pdf_5(self):
        self.assertEqual(DataStatistics4.pdf([1, 2, 3], 2, 2),
                         [0.17603266338214976, 0.19947114020071635, 0.17603266338214976])


class DataStatistics4TestMain(unittest.TestCase):
    def test_main(self):
        self.assertEqual(DataStatistics4.correlation_coefficient([1, 2, 3], [4, 5, 6]), 0.9999999999999998)
        self.assertEqual(DataStatistics4.skewness([1, 2, 5]), 2.3760224064818463)
        self.assertEqual(DataStatistics4.kurtosis([1, 2, 5]), -1.5000000000000002)
        self.assertEqual(DataStatistics4.pdf([1, 2, 3], 1, 1),
                         [0.3989422804014327, 0.24197072451914337, 0.05399096651318806])