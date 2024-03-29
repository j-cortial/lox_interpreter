import lox.stmt as stmt
from lox.stmt import Block, Class, Expression, Print, Return, Stmt, Var, If, While
import lox.expr as expr
from lox.expr import (
    Assign,
    Binary,
    Set,
    Super,
    This,
    Unary,
    Expr,
    Grouping,
    Literal,
    Variable,
)
from lox.tokens import Token
from lox.token_types import TokenType
from lox.runtime_error import InterpreterRuntimeError
from lox.return_value import ReturnValue
from lox.environment import Environment
from lox.lox_callable import LoxCallable
from lox.lox_function import LoxFunction
from lox.lox_class import LoxClass
from lox.lox_instance import LoxInstance

from typing import NoReturn, Optional
import time


class Interpreter(stmt.Visitor, expr.Visitor):
    def __init__(self) -> None:
        self.globals: Environment = Environment()
        self.environment: Environment = self.globals
        self.locals: dict[Expr, int] = dict()

        class NativeClock(LoxCallable):
            def arity(self) -> int:
                return 0

            def call(self, interpreter: Interpreter, arguments: list[object]) -> float:
                return time.time()

            def __str__(self) -> str:
                return "<native fn>"

        self.globals.define("clock", NativeClock())

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except InterpreterRuntimeError as error:
            import lox.__main__ as __main__

            __main__.runtime_error(error)

    def execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def resolve(self, expr: Expr, depth: int) -> None:
        self.locals[expr] = depth

    def execute_block(self, statements: list[Stmt], environment: Environment) -> None:
        previous: Environment = self.environment
        try:
            self.environment: Environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_block_stmt(self, stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_class_stmt(self, stmt: Class) -> None:
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise InterpreterRuntimeError(
                    stmt.superclass.name, "Superclass must be a class"
                )
        self.environment.define(stmt.name.lexeme, None)
        if superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)
        methods: dict[str, LoxFunction] = {}
        for method in stmt.methods:
            function = LoxFunction(
                method, self.environment, method.name.lexeme == "init"
            )
            methods[method.name.lexeme] = function
        klass = LoxClass(stmt.name.lexeme, superclass, methods)
        if superclass is not None:
            enclosing = self.environment.enclosing
            assert enclosing is not None
            self.environment = enclosing
        self.environment.assign(stmt.name, klass)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: stmt.Function) -> None:
        function: LoxFunction = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)

    def visit_if_stmt(self, stmt: If) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_return_stmt(self, stmt: Return) -> NoReturn:
        value: Optional[object] = (
            self.evaluate(stmt.value) if stmt.value is not None else None
        )
        raise ReturnValue(value)

    def visit_var_stmt(self, stmt: Var) -> None:
        value: Optional[object] = (
            self.evaluate(stmt.initializer) if stmt.initializer is not None else None
        )
        self.environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: While) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_assign_expr(self, expr: Assign):
        value = self.evaluate(expr.value)
        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    def visit_logical_expr(self, expr: expr.Logical):
        left = self.evaluate(expr.left)
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return self.evaluate(expr.right)

    def visit_set_expr(self, expr: Set):
        instance: object = self.evaluate(expr.instance)
        if not isinstance(instance, LoxInstance):
            raise InterpreterRuntimeError(expr.name, "Only instances have fields")
        value: object = self.evaluate(expr.value)
        instance.set(expr.name, value)
        return value

    def visit_super_expr(self, expr: Super) -> LoxFunction:
        distance = self.locals[expr]
        superclass = self.environment.get_at(distance, "super")
        assert isinstance(superclass, LoxClass)
        instance = self.environment.get_at(distance - 1, "this")
        assert isinstance(instance, LoxInstance)
        method = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise InterpreterRuntimeError(
                expr.method, f"Undefined property {expr.method.lexeme}"
            )
        return method.bind(instance)

    def visit_this_expr(self, expr: This) -> object:
        return self.lookup_variable(expr.keyword, expr)

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
        return

    def visit_variable_expr(self, expr: Variable) -> object:
        return self.lookup_variable(expr.name, expr)

    def lookup_variable(self, name: Token, expr: Expr) -> object:
        distance: Optional[int] = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def check_number_operand(self, operator: Token, operand: object) -> None:
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
        return

    def visit_call_expr(self, expr: expr.Call) -> object:
        callee: object = self.evaluate(expr.callee)
        arguments: list[object] = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        from lox.lox_callable import LoxCallable

        if not isinstance(callee, LoxCallable):
            raise InterpreterRuntimeError(
                expr.paren, "Can only call functions and classes"
            )
        function: LoxCallable = callee
        if len(arguments) != function.arity():
            raise InterpreterRuntimeError(
                expr.paren,
                f"Expected {function.arity()} arguments but got {len(arguments)}",
            )
        return function.call(self, arguments)

    def visit_get_expr(self, expr: expr.Get) -> object:
        instance: object = self.evaluate(expr.instance)
        if isinstance(instance, LoxInstance):
            return instance.get(expr.name)
        raise InterpreterRuntimeError(expr.name, "Only instances have properties")

    def check_number_operands(
        self, operator: Token, left: object, right: object
    ) -> None:
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
