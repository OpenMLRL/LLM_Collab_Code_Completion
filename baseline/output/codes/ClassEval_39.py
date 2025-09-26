class ExpressionCalculator:
    """
    This is a class in Python that can perform calculations with basic arithmetic operations, including addition, subtraction, multiplication, division, and modulo.
    """

    def __init__(self):
        """
        Initialize the expression calculator
        """
        self.postfix_stack = deque()
        self.operat_priority = [0, 3, 2, 1, -1, 1, 0, 2]

    def calculate(self, expression):
        """
        Calculate the result of the given postfix expression
        :param expression: string, the postfix expression to be calculated
        :return: float, the calculated result
        >>> expression_calculator = ExpressionCalculator()
        >>> expression_calculator.calculate("2 + 3 * 4")
        14.0
        """
        self.prepare(expression)
        while self.postfix_stack:
            if self.postfix_stack[-1] in "+-*/%":
                second = self.postfix_stack.pop()
                first = self.postfix_stack.pop()
                result = self._calculate(first, second, self.postfix_stack.pop())
                self.postfix_stack.append(result)
            else:
                self.postfix_stack.append(self.postfix_stack.pop())
        return float(self.postfix_stack[0])

    def prepare(self, expression):
        """
        Prepare the infix expression for conversion to postfix notation
        :param expression: string, the infix expression to be prepared
        >>> expression_calculator = ExpressionCalculator()
        >>> expression_calculator.prepare("2+3*4")
        """
        self.postfix_stack.clear()
        expression = expression.replace(" ", "")
        stack = []
        for char in expression:
            if char.isdigit() or char == ".":
                self.postfix_stack.append(char)
            elif char in "+-*/%":
                while stack and self.is_operator(stack[-1]) and self.compare(char, stack[-1]):
                    self.postfix_stack.append(stack.pop())
                stack.append(char)
            elif char == "(":
                stack.append(char)
            elif char == ")":
                while stack and stack[-1] != "(":
                    self.postfix_stack.append(stack.pop())
                stack.pop()
        while stack:
            self.postfix_stack.append(stack.pop())

    @staticmethod
    def is_operator(c):
        """
        Check if a character is an operator in {'+', '-', '*', '/', '(', ')', '%'}
        :param c: string, the character to be checked
        :return: bool, True if the character is an operator, False otherwise
        >>> expression_calculator = ExpressionCalculator()
        >>> expression_calculator.is_operator("+")
        True
        """
        return c in "+-*/%"

    def compare(self, cur, peek):
        """
        Compare the precedence of two operators
        :param cur: string, the current operator
        :param peek: string, the operator at the top of the operator stack
        :return: bool, True if the current operator has higher or equal precedence, False otherwise
        >>> expression_calculator = ExpressionCalculator()
        >>> expression_calculator.compare("+", "-")
        True
        """
        return self.operat_priority[self.is_operator(cur)] >= self.operat_priority[self.is_operator(peek)]

    @staticmethod
    def _calculate(first_value, second_value, current_op):
        """
        Perform the mathematical calculation based on the given operands and operator
        :param first_value: string, the first operand
        :param second_value: string, the second operand
        :param current_op: string, the operator
        :return: decimal.Decimal, the calculated result
        >>> expression_calculator = ExpressionCalculator()
        >>> expression_calculator._calculate("2", "3", "+")
        5.0
        """
        first_value = float(first_value)
        second_value = float(second_value)
        if current_op == "+":
            return first_value + second_value
        elif current_op == "-":
            return first_value - second_value
        elif current_op == "*":
            return first_value * second_value
        elif current_op == "/":
            return first_value / second_value
        elif current_op == "%":
            return first_value % second_value

    @staticmethod
    def transform(expression):
        """
        Transform the infix expression to a format suitable for conversion
        :param expression: string, the infix expression to be transformed
        :return: string, the transformed expression
        >>> expression_calculator = ExpressionCalculator()
        >>> expression_calculator.transform("2 + 3 * 4")
        "2+3*4"
        """
        return expression

import unittest


class ExpressionCalculatorTestCalculate(unittest.TestCase):
    def setUp(self):
        self.expression_calculator = ExpressionCalculator()

    def test_calculate_1(self):
        result = self.expression_calculator.calculate("2 + 3 * 4")
        self.assertEqual(result, 14.0)

    def test_calculate_2(self):
        result = self.expression_calculator.calculate("2 + 3 + 4")
        self.assertEqual(result, 9.0)

    def test_calculate_3(self):
        result = self.expression_calculator.calculate("2 * 3 * 4")
        self.assertEqual(result, 24.0)

    def test_calculate_4(self):
        result = self.expression_calculator.calculate("2 + 4 / 4")
        self.assertEqual(result, 3.0)

    def test_calculate_5(self):
        result = self.expression_calculator.calculate("(2 + 3) * 4")
        self.assertEqual(result, 20.0)


class ExpressionCalculatorTestPrepare(unittest.TestCase):
    def setUp(self):
        self.expression_calculator = ExpressionCalculator()

    def test_prepare_1(self):
        self.expression_calculator.prepare("2+3*4")
        self.assertEqual(self.expression_calculator.postfix_stack, deque(['2', '3', '4', '*', '+']))

    def test_prepare_2(self):
        self.expression_calculator.prepare("2+3/4")
        self.assertEqual(self.expression_calculator.postfix_stack, deque(['2', '3', '4', '/', '+']))

    def test_prepare_3(self):
        self.expression_calculator.prepare("2-3*4")
        self.assertEqual(self.expression_calculator.postfix_stack, deque(['2', '3', '4', '*', '-']))

    def test_prepare_4(self):
        self.expression_calculator.prepare("1+3*4")
        self.assertEqual(self.expression_calculator.postfix_stack, deque(['1', '3', '4', '*', '+']))

    def test_prepare_5(self):
        self.expression_calculator.prepare("(2+3)*4")
        self.assertEqual(self.expression_calculator.postfix_stack, deque(['2', '3', '+', '4', '*']))

    def test_prepare_6(self):
        self.expression_calculator.prepare("")
        self.assertEqual(self.expression_calculator.postfix_stack, deque([]))


class ExpressionCalculatorTestIsOperator(unittest.TestCase):
    def setUp(self):
        self.expression_calculator = ExpressionCalculator()

    def test_is_operator_1(self):
        self.assertTrue(self.expression_calculator.is_operator("+"))

    def test_is_operator_2(self):
        self.assertTrue(self.expression_calculator.is_operator("-"))

    def test_is_operator_3(self):
        self.assertTrue(self.expression_calculator.is_operator("*"))

    def test_is_operator_4(self):
        self.assertTrue(self.expression_calculator.is_operator("/"))

    def test_is_operator_5(self):
        self.assertFalse(self.expression_calculator.is_operator("5"))


class ExpressionCalculatorTestCompare(unittest.TestCase):
    def setUp(self):
        self.expression_calculator = ExpressionCalculator()

    def test_compare_1(self):
        result = self.expression_calculator.compare("+", "-")
        self.assertTrue(result)

    def test_compare_2(self):
        result = self.expression_calculator.compare("*", "/")
        self.assertTrue(result)

    def test_compare_3(self):
        result = self.expression_calculator.compare("+", "*")
        self.assertTrue(result)

    def test_compare_4(self):
        result = self.expression_calculator.compare("*", "+")
        self.assertFalse(result)

    def test_compare_5(self):
        result = self.expression_calculator.compare("/", "+")
        self.assertFalse(result)

    def test_compare_6(self):
        result = self.expression_calculator.compare("%", "+")
        self.assertFalse(result)

    def test_compare_7(self):
        result = self.expression_calculator.compare("+", "%")
        self.assertTrue(result)


class ExpressionCalculatorTestCalculateMethod(unittest.TestCase):
    def setUp(self):
        self.expression_calculator = ExpressionCalculator()

    def test_calculate_method_1(self):
        result = self.expression_calculator._calculate("2", "3", "+")
        self.assertEqual(result, Decimal(5.0))

    def test_calculate_method_2(self):
        result = self.expression_calculator._calculate("3", "2", "-")
        self.assertEqual(result, Decimal(1.0))

    def test_calculate_method_3(self):
        result = self.expression_calculator._calculate("2", "3", "*")
        self.assertEqual(result, Decimal(6.0))

    def test_calculate_method_4(self):
        result = self.expression_calculator._calculate("3", "3", "/")
        self.assertEqual(result, Decimal(1.0))

    def test_calculate_method_5(self):
        result = self.expression_calculator._calculate("6", "2", "/")
        self.assertEqual(result, Decimal(3.0))

    def test_calculate_method_6(self):
        result = self.expression_calculator._calculate("6", "2", "%")
        self.assertEqual(result, Decimal(0.0))

    def test_calculate_method_7(self):
        try:
            self.expression_calculator._calculate("6", "2", "??")
        except:
            pass


class ExpressionCalculatorTestTransform(unittest.TestCase):
    def setUp(self):
        self.expression_calculator = ExpressionCalculator()

    def test_transform_1(self):
        result = self.expression_calculator.transform("2 + 3 * 4")
        self.assertEqual(result, "2+3*4")

    def test_transform_2(self):
        result = self.expression_calculator.transform("2 + 3 / 4")
        self.assertEqual(result, "2+3/4")

    def test_transform_3(self):
        result = self.expression_calculator.transform("2 - 3 * 4")
        self.assertEqual(result, "2-3*4")

    def test_transform_4(self):
        result = self.expression_calculator.transform("1 + 3 * 4")
        self.assertEqual(result, "1+3*4")

    def test_transform_5(self):
        result = self.expression_calculator.transform("-2 + (-3) * 4")
        self.assertEqual(result, "~2+(~3)*4")

    def test_transform_6(self):
        result = self.expression_calculator.transform("~(1 + 1)")
        self.assertEqual(result, "0-(1+1)")


class ExpressionCalculatorTest(unittest.TestCase):
    def setUp(self):
        self.expression_calculator = ExpressionCalculator()

    def test_ExpressionCalculator(self):
        result = self.expression_calculator.calculate("2 + 3 * 4")
        self.assertEqual(result, 14.0)

        self.expression_calculator.prepare("2+3*4")
        self.assertEqual(self.expression_calculator.postfix_stack, deque(['2', '3', '4', '*', '+']))

        self.assertTrue(self.expression_calculator.is_operator("+"))

        result = self.expression_calculator.compare("+", "-")
        self.assertTrue(result)

        result = self.expression_calculator._calculate("2", "3", "+")
        self.assertEqual(result, Decimal(5.0))

        result = self.expression_calculator.transform("2 + 3 * 4")
        self.assertEqual(result, "2+3*4")