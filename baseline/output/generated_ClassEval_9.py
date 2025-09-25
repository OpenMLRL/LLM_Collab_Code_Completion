class BigNumCalculator:
    """
    This is a class that implements big number calculations, including adding, subtracting and multiplying.
    """

    @staticmethod
    def add(num1, num2):
        """
        Adds two big numbers.
        :param num1: The first number to add,str.
        :param num2: The second number to add,str.
        :return: The sum of the two numbers,str.
        >>> bigNum = BigNumCalculator()
        >>> bigNum.add("12345678901234567890", "98765432109876543210")
        '111111111011111111100'

        """

    @staticmethod
    def subtract(num1, num2):
        """
        Subtracts two big numbers.
        :param num1: The first number to subtract,str.
        :param num2: The second number to subtract,str.
        :return: The difference of the two numbers,str.
        >>> bigNum = BigNumCalculator()
        >>> bigNum.subtract("12345678901234567890", "98765432109876543210")
        '-86419753208641975320'

        """

    @staticmethod
    def multiply(num1, num2):
        """
        Multiplies two big numbers.
        :param num1: The first number to multiply,str.
        :param num2: The second number to multiply,str.
        :return: The product of the two numbers,str.
        >>> bigNum = BigNumCalculator()
        >>> bigNum.multiply("12345678901234567890", "98765432109876543210")
        '1219326311370217952237463801111263526900'

        """

from functools import reduce

def add(num1, num2):
    return str(reduce(lambda x, y: x + y, map(int, list(num1 + num2))))

def subtract(num1, num2):
    return str(reduce(lambda x, y: x - y, map(int, list(num1 + num2))))

def multiply(num1, num2):
    return str(reduce(lambda x, y: x * y, map(int, list(num1 + num2))))
# Test cases
bigNum = BigNumCalculator()
assert add("12345678901234567890", "98765432109876543210") == "111111111011111111100"
assert subtract("12345678901234567890", "98765432109876543210") == "-86419753208641975320"
assert multiply("12345678901234567890", "98765432109876543210") == "1219326311370217952237463801111263526900"
