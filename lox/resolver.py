from enum import Enum
import lox.__main__
import lox.expr as expr
import lox.stmt as stmt
from lox.interpreter import Interpreter
from lox.expr import (
    Assign,
    Binary,
    Call,
    Expr,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from lox.stmt import Expression, Function, If, Print, Return, Stmt, Block, Var, While
from lox.tokens import Token

FunctionType = Enum("FunctionType", ["NONE", "FUNCTION"])


class Resolver(expr.Visitor, stmt.Visitor):
    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter: Interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.current_function: FunctionType = FunctionType.NONE

    def visit_block_stmt(self, stmt: Block) -> None:
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.resolve_expr(stmt.expression)

    def visit_function_stmt(self, stmt: Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_if_stmt(self, stmt: If) -> None:
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_stmt(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        self.resolve_expr(stmt.expression)

    def visit_return_stmt(self, stmt: Return) -> None:
        if self.current_function == FunctionType.NONE:
            lox.__main__.error(stmt.keyword.line, "Cannot return from top-level code")
        if stmt.value is not None:
            self.resolve_expr(stmt.value)

    def visit_var_stmt(self, stmt: Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve_expr(stmt.initializer)
        self.define(stmt.name)

    def visit_while_stmt(self, stmt: While) -> None:
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)

    def visit_binary_expression(self, expr: Binary) -> None:
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_call_expression(self, expr: Call) -> None:
        self.resolve_expr(expr.callee)
        for argument in expr.arguments:
            self.resolve_expr(argument)

    def visit_grouping_expression(self, expr: Grouping) -> None:
        self.resolve_expr(expr.expression)

    def visit_literal_expression(self, expr: Literal) -> None:
        pass

    def visit_logical_expression(self, expr: Logical) -> None:
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_unary_expr(self, expr: Unary):
        self.resolve_expr(expr.right)

    def visit_variable_expr(self, expr: Variable) -> None:
        if len(self.scopes) >= 1 and self.scopes[-1].get(expr.name.lexeme) is False:
            lox.__main__.error(
                expr.name.line, "Cannot read local variable in its own initializer"
            )
        self.resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr: Assign) -> None:
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)

    def resolve(self, statements: list[Stmt]) -> None:
        for statement in statements:
            self.resolve_stmt(statement)

    def resolve_function(self, function: Function, type: FunctionType) -> None:
        enclosing_function: FunctionType = self.current_function
        self.current_function = type
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def resolve_stmt(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def resolve_expr(self, expr: Expr) -> None:
        expr.accept(self)

    def begin_scope(self) -> None:
        self.scopes.append(dict())

    def end_scope(self) -> None:
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return
        scope: dict[str, bool] = self.scopes[-1]
        if name.lexeme in scope:
            lox.__main__.error(
                name.line, "Already a variable with this name in this scope"
            )
        scope[name.lexeme] = False

    def define(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return
        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr: Expr, name: Token) -> None:
        for n, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, n)
                return
