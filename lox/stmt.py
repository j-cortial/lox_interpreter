from lox.expr import Expr


class Stmt:
    def accept(self, visitor):
        raise NotImplementedError


class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)


class Visitor:
    def visit_expression_stmt(self, stmt: Expression):
        raise NotImplementedError

    def visit_print_stmt(self, stmt: Print):
        raise NotImplementedError
