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