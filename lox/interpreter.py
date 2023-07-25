from lox.expr import Binary, Unary, Visitor, Expr, Grouping, Literal
from lox.tokens import Token
from lox.token_types import TokenType
from lox.runtime_error import InterpreterRuntimeError

class Interpreter(Visitor):
    def interpret(self, expression: Expr):
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))
        except InterpreterRuntimeError as error:
            import lox.__main__ as __main__

            __main__.runtime_error(error)

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    def visit_grouping_expr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: Unary):
        right = self.evaluate(expr.right)
        match expr.operator.type:
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -right
        # Unreachable
        return None

    def check_number_operand(self, operator: Token, operand: object):
        if type(operand) is float:
            return
        raise InterpreterRuntimeError(operator, "Operand must be a number")

    def is_truthy(self, obj: object) -> bool:
        if obj is None:
            return False
        if type(obj) is bool:
            return obj
        return True

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, right, left)
                return left > right
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, right, left)
                return left >= right
            case TokenType.LESS:
                self.check_number_operands(expr.operator, right, left)
                return left < right
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, right, left)
                return left <= right
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, right, left)
                return left - right
            case TokenType.PLUS:
                if type(left) is str and type(right) is str:
                    return left + right
                if type(left) is float and type(right) is float:
                    return left + right
                raise InterpreterRuntimeError(
                    expr.operator, "Operands must be a two numbers or two strings"
                )
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, right, left)
                return left / right
            case TokenType.STAR:
                self.check_number_operands(expr.operator, right, left)
                return left * right

        # Unreachable
        return None

    def check_number_operands(self, operator: Token, left: object, right: object):
        if type(left) is float and type(right) is float:
            return
        raise InterpreterRuntimeError(operator, "Operands must be numbers")

    def is_equal(self, a: object, b: object) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def stringify(self, obj) -> str:
        if obj is None:
            return "nil"
        if type(obj) is float:
            text: str = str(obj)
            if text.endswith(".0"):
                text = text[0:-2]
            return text
        return str(obj)
