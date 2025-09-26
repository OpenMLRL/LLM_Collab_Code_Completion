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

        # Perform addition from right to left
        carry = 0
        for i in range(max_length - 1, -1, -1):
            total = num1_list[i] + num2_list[i] + carry
            carry = total // 10
            result.insert(0, total % 10)

        # Add any remaining carry
        if carry:
            result.insert(0, carry)

        # Convert the result list back to a string
        return ''.join(map(str, result))

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

        # Perform subtraction from right to left
        carry = 0
        for i in range(max_length - 1, -1, -1):
            diff = num1_list[i] - num2_list[i] - carry
            if diff < 0:
                diff += 10
                carry = 1
            else:
                carry = 0
            result.insert(0, diff)

        # Remove leading zeros
        result = ''.join(map(str, result)).lstrip('0')

        # If the result is empty, it means num1 was greater than num2
        if not result:
            return '-'

        return result

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
        result = [0] * (len(num1_list) + len(num2_list