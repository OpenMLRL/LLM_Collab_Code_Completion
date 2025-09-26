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
        mean1 = sum(data1) / len(data1)
        mean2 = sum(data2) / len(data2)
        std1 = math.sqrt(sum((x - mean1) ** 2 for x in data1) / len(data1))
        std2 = math.sqrt(sum((y - mean2) ** 2 for y in data2) / len(data2))
        covariance = sum((x - mean1) * (y - mean2) for x, y in zip(data1, data2)) / len(data1)
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
        mean = sum(data) / len(data)
        std = math.sqrt(sum((x - mean) ** 2 for x in data) / len(data))
        return sum((x - mean) ** 3 for x in data) / (len(data) * std ** 3)

    @staticmethod
    def kurtosis(data):
        """
        Calculate the kurtosis of a set of data.
        :param data: The input data list, list.
        :return: The kurtosis, float.
        >>> DataStatistics4.kurtosis([1, 20, 100])
        -1.5000000000000007
        """
        mean = sum(data) / len(data)
        std = math.sqrt(sum((x - mean) ** 2 for x in data) / len(data))
        return sum((x - mean) ** 4 for x in data) / (len(data) * std ** 4) - 3

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