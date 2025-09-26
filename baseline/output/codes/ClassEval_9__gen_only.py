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
        # Convert strings to lists of digits
        num1_list = [int(digit) for digit in num1]
        num2_list = [int(digit) for digit in num2]

        # Pad the shorter list with zeros
        max_len = max(len(num1_list), len(num2_list))
        num1_list += [0] * (max_len - len(num1_list))
        num2_list += [0] * (max_len - len(num2_list))

        # Initialize the result list
        result = []

        # Perform addition
        carry = 0
        for i in range(max_len - 1, -1, -1):
            digit_sum = num1_list[i] + num2_list[i] + carry
            result.append(digit_sum % 10)
            carry = digit_sum // 10

        # Add any remaining carry
        if carry:
            result.append(carry)

        # Convert the result list to a string
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
        # Convert strings to lists of digits
        num1_list = [int(digit) for digit in num1]
        num2_list = [int(digit) for digit in num2]

        # Pad the shorter list with zeros
        max_len = max(len(num1_list), len(num2_list))
        num1_list += [0] * (max_len - len(num1_list))
        num2_list += [0] * (max_len - len(num2_list))

        # Initialize the result list
        result = []

        # Perform subtraction
        carry = 0
        for i in range(max_len - 1, -1, -1):
            digit_diff = num1_list[i] - num2_list[i] - carry
            if digit_diff < 0:
                digit_diff += 10
                carry = 1
            else:
                carry = 0
            result.append(digit_diff)

        # Remove leading zeros
        while result and result[0] == 0:
            result.pop(0)

        # Convert the result list to a string
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
        # Convert strings to lists of digits
        num1_list = [int(digit) for digit in num1]
        num2_list = [int(digit) for digit in num2]

        # Initialize the result list
        result = [0] * (len(num1_list) + len(num2_list))

        # Perform multiplication
        for i in range(len(num1_list)):
            for j in range(len(num2_list)):
                result[i + j] += num1_list[i] * num2_list[j]

        # Perform carry propagation
        carry = 0
        for i in range(len(result) - 1, -1, -1):
            digit_sum = result[i] + carry
            result[i] = digit_sum % 10
            carry = digit_sum // 10

        # Remove leading zeros
        while result and result[0] == 0:
            result.pop(0)

        # Convert the result list to a string
        return ''.join(str(digit) for digit in result[::-1])