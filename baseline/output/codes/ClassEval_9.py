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
        # Convert strings to lists of integers
        num1_list = [int(digit) for digit in num1]
        num2_list = [int(digit) for digit in num2]

        # Pad the shorter list with zeros
        max_length = max(len(num1_list), len(num2_list))
        num1_list += [0] * (max_length - len(num1_list))
        num2_list += [0] * (max_length - len(num2_list))

        # Initialize the result list
        result = []

        # Perform addition
        carry = 0
        for i in range(max_length - 1, -1, -1):
            sum_digits = num1_list[i] + num2_list[i] + carry
            result.append(sum_digits % 10)
            carry = sum_digits // 10

        # Add any remaining carry
        if carry:
            result.append(carry)

        # Convert the result list back to a string
        return ''.join(str(digit) for digit in result[::-1])

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
        # Convert strings to lists of integers
        num1_list = [int(digit) for digit in num1]
        num2_list = [int(digit) for digit in num2]

        # Pad the shorter list with zeros
        max_length = max(len(num1_list), len(num2_list))
        num1_list += [0] * (max_length - len(num1_list))
        num2_list += [0] * (max_length - len(num2_list))

        # Initialize the result list
        result = []

        # Perform subtraction
        carry = 0
        for i in range(max_length - 1, -1, -1):
            diff_digits = num1_list[i] - num2_list[i] - carry
            if diff_digits < 0:
                diff_digits += 10
                carry = 1
            else:
                carry = 0
            result.append(diff_digits)

        # Remove leading zeros
        while result and result[0] == 0:
            result.pop(0)

        # Convert the result list back to a string
        return ''.join(str(digit) for digit in result[::-1])

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
        # Convert strings to lists of integers
        num1_list = [int(digit) for digit in num1]
        num2_list = [int(digit) for digit in num2]

        # Initialize the result list
        result = [0] * (len(num1_list) + len(num2_list))

        # Perform multiplication
        for i in range(len(num1_list)):
            for j in range(len(num2_list)):
                result[i + j] += num1_list[i] * num2_list[j]

        # Perform addition to handle carry
        carry = 0
        for i in range(len(result)):
            result[i] += carry
            carry = result[i] // 10
            result[i] %= 10

        # Remove leading zeros
        while result and result[0] == 0:
            result.pop(0)

        # Convert the result list back to a string
        return ''.join(str(digit) for digit in result[::-1])

import unittest

class BigNumCalculatorTestAdd(unittest.TestCase):
    def test_add(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.add("12345678901234567890", "98765432109876543210"), "111111111011111111100")

    def test_add_2(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.add("123456789012345678922", "98765432109876543210"), "222222221122222222132")

    def test_add_3(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.add("123456789012345678934", "98765432109876543210"), "222222221122222222144")

    def test_add_4(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.add("123456789012345678946", "98765432109876543210"), "222222221122222222156")

    def test_add_5(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.add("123456789012345678958", "98765432109876543210"), "222222221122222222168")

class BigNumCalculatorTestSubtract(unittest.TestCase):
    def test_subtract(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.subtract("12345678901234567890", "98765432109876543210"), "-86419753208641975320")

    def test_subtract_2(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.subtract("123456789012345678922", "98765432109876543210"), "24691356902469135712")

    def test_subtract_3(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.subtract("123456789012345678934", "98765432109876543"), "123358023580235802391")

    def test_subtract_4(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.subtract("12345678901234567", "98765432109876543210"), "-98753086430975308643")

    def test_subtract_5(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.subtract("923456789", "187654321"), "735802468")

class BigNumCalculatorTestMultiply(unittest.TestCase):
    def test_multiply(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.multiply("12345678901234567890", "98765432109876543210"), "1219326311370217952237463801111263526900")

    def test_multiply_2(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.multiply("123456789012345678922", "98765432109876543210"), "12193263113702179524547477517529919219620")

    def test_multiply_3(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.multiply("123456789012345678934", "98765432109876543"), "12193263113702179499806737010255845162")

    def test_multiply_4(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.multiply("12345678901234567", "98765432109876543210"), "1219326311370217864336229223321140070")

    def test_multiply_5(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.multiply("923456789", "187654321"), "173290656712635269")

    def test_multiply_6(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.multiply("000000001", "000000001"), "1")

class BigNumCalculatorTestMain(unittest.TestCase):
    def test_main(self):
        bigNum = BigNumCalculator()
        self.assertEqual(bigNum.add("12345678901234567890", "98765432109876543210"), "111111111011111111100")
        self.assertEqual(bigNum.subtract("12345678901234567890", "98765432109876543210"), "-86419753208641975320")
        self.assertEqual(bigNum.multiply("12345678901234567890", "98765432109876543210"), "1219326311370217952237463801111263526900")