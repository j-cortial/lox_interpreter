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
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Super,
    This,
    Unary,
    Variable,
)
from lox.stmt import (
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Stmt,
    Block,
    Var,
    While,
)
from lox.tokens import Token

FunctionType = Enum("FunctionType", ["NONE", "INITIALIZER", "METHOD", "FUNCTION"])
ClassType = Enum("ClassType", ["NONE", "SUBCLASS", "CLASS"])


class Resolver(expr.Visitor, stmt.Visitor):
    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.current_function: FunctionType = FunctionType.NONE
        self.current_class: ClassType = ClassType.NONE

    def visit_block_stmt(self, stmt: Block) -> None:
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    def visit_class_stmt(self, stmt: Class) -> None:
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        self.declare(stmt.name)
        self.define(stmt.name)
        if (
            stmt.superclass is not None
            and stmt.name.lexeme == stmt.superclass.name.lexeme
        ):
            lox.__main__.error(
                stmt.superclass.name.line, "A class cannot inherit from itself"
            )
        if stmt.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            self.resolve_expr(stmt.superclass)
        if stmt.superclass is not None:
            self.begin_scope()
            self.scopes[-1]["super"] = True
        self.begin_scope()
        self.scopes[-1]["this"] = True
        for method in stmt.methods:
            declaration = (
                FunctionType.INITIALIZER
                if method.name.lexeme == "init"
                else FunctionType.METHOD
            )
            self.resolve_function(method, declaration)
        self.end_scope()
        if stmt.superclass is not None:
            self.end_scope()
        self.current_class = enclosing_class

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
            if self.current_function == FunctionType.INITIALIZER:
                lox.__main__.error(
                    stmt.keyword.line, "Cannot return a value from an initializer"
                )
            self.resolve_expr(stmt.value)

    def visit_var_stmt(self, stmt: Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve_expr(stmt.initializer)
        self.define(stmt.name)

    def visit_while_stmt(self, stmt: While) -> None:
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)

    def visit_binary_expr(self, expr: Binary) -> None:
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_call_expr(self, expr: Call) -> None:
        self.resolve_expr(expr.callee)
        for argument in expr.arguments:
            self.resolve_expr(argument)

    def visit_get_expr(self, expr: Get) -> None:
        self.resolve_expr(expr.instance)

    def visit_grouping_expr(self, expr: Grouping) -> None:
        self.resolve_expr(expr.expression)

    def visit_literal_expr(self, expr: Literal) -> None:
        pass

    def visit_logical_expr(self, expr: Logical) -> None:
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_set_expr(self, expr: Set) -> None:
        self.resolve_expr(expr.value)
        self.resolve_expr(expr.instance)

    def visit_super_expr(self, expr: Super) -> None:
        if self.current_class == ClassType.NONE:
            lox.__main__.error(
                expr.keyword.line, "Cannot use 'super' outside of a class"
            )
        elif self.current_class != ClassType.SUBCLASS:
            lox.__main__.error(
                expr.keyword.line, "Cannot use 'super' in a class without superclass"
            )
        self.resolve_local(expr, expr.keyword)

    def visit_this_expr(self, expr: This) -> None:
        if self.current_class == ClassType.NONE:
            lox.__main__.error(
                expr.keyword.line, "Cannot use 'this' outside of a class"
            )
        self.resolve_local(expr, expr.keyword)

    def visit_unary_expr(self, expr: Unary) -> None:
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
