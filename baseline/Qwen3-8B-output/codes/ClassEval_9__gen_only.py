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
        # Convert strings to integers
        num1_int = int(num1)
        num2_int = int(num2)
        # Perform addition
        result = num1_int + num2_int
        # Convert back to string and return
        return str(result)

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
        # Convert strings to integers
        num1_int = int(num1)
        num2_int = int(num2)
        # Perform subtraction
        result = num1_int - num2_int
        # Convert back to string and return
        return str(result)

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
        # Convert strings to integers
        num1_int = int(num1)
        num2_int = int(num2)
        # Perform multiplication
        result = num1_int * num2_int
        # Convert back to string and return
        return str(result)