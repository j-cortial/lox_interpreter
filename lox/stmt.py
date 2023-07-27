from lox.expr import Expr
from lox.tokens import Token


class Stmt:
    def accept(self, visitor):
        raise NotImplementedError


class Block(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)


class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr | None):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)


class Visitor:
    def visit_block_stmt(self, stmt: Block):
        raise NotImplementedError

    def visit_expression_stmt(self, stmt: Expression):
        raise NotImplementedError

    def visit_print_stmt(self, stmt: Print):
        raise NotImplementedError

    def visit_var_stmt(self, stmt: Var):
        raise NotImplementedError
