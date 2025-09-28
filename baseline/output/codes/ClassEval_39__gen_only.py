from collections import deque
import decimal

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
        for token in expression.split():
            if token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
                self.postfix_stack.append(decimal.Decimal(token))
            else:
                if token == '(':
                    self.postfix_stack.append(token)
                else:
                    if token == ')':
                        while self.postfix_stack and self.postfix_stack[-1] != '(':
                            self.postfix_stack.append(self.postfix_stack.pop())
                        self.postfix_stack.pop()  # Remove '('
                    else:
                        while self.postfix_stack and self.postfix_stack[-1] != '(' and self.compare(token, self.postfix_stack[-1]):
                            self.postfix_stack.append(self.postfix_stack.pop())
                        self.postfix_stack.append(token)
        while self.postfix_stack:
            if self.postfix_stack[-1] == '(':
                self.postfix_stack.pop()
            else:
                break
        result = self._calculate(self.postfix_stack.pop(), self.postfix_stack.pop(), self.postfix_stack.pop())
        return float(result)

    def prepare(self, expression):
        """
        Prepare the infix expression for conversion to postfix notation
        :param expression: string, the infix expression to be prepared
        >>> expression_calculator = ExpressionCalculator()
        >>> expression_calculator.prepare("2+3*4")
        expression_calculator.postfix_stack = ['2', '3', '4', '*', '+']
        """
        tokens = self.transform(expression)
        for token in tokens:
            if token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
                self.postfix_stack.append(token)
            else:
                if token == '(':
                    self.postfix_stack.append(token)
                else:
                    if token == ')':
                        while self.postfix_stack and self.postfix_stack[-1] != '(':
                            self.postfix_stack.append(self.postfix_stack.pop())
                        self.postfix_stack.pop()  # Remove '('
                    else:
                        while self.postfix_stack and self.postfix_stack[-1] != '(' and self.compare(token, self.postfix_stack[-1]):
                            self.postfix_stack.append(self.postfix_stack.pop())
                        self.postfix_stack.append(token)
        while self.postfix_stack:
            if self.postfix_stack[-1] == '(':
                self.postfix_stack.pop()
            else:
                break

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
        return c in {'+', '-', '*', '/', '(', ')', '%'}

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
        cur_priority = self.operat_priority[0] if cur == '(' else self.operat_priority[1] if cur == '+' else self.operat_priority[2] if cur == '-' else self.operat_priority[3] if cur == '*' else self.operat_priority[4] if cur == '/' else self.operat_priority[5] if cur == '%' else 0
        peek_priority = self.operat_priority[0] if peek == '(' else self.operat_priority[1] if peek == '+' else self.operat_priority[2] if peek == '-' else self.operat_priority[3] if peek == '*' else self.operat_priority[4] if peek == '/' else self.operat_priority[5] if peek == '%' else 0
        return cur_priority >= peek_priority

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
        a = decimal.Decimal(first_value)
        b = decimal.Decimal(second_value)
        if current_op == '+':
            return a + b
        elif current_op == '-':
            return a - b
        elif current_op == '*':
            return a * b
        elif current_op == '/':
            return a / b
        elif current_op == '%':
            return a % b
        else:
            raise ValueError("Unknown operator")

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
        return expression.replace(' ', '')