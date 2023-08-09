from lox.tokens import Token
from typing import TypeAlias

VisitorFwd: TypeAlias = "Visitor"


class Expr:
    def accept(self, visitor: VisitorFwd):
        raise NotImplementedError


class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor: VisitorFwd):
        return visitor.visit_assign_expr(self)


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: VisitorFwd):
        return visitor.visit_binary_expr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: VisitorFwd):
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self, value: object):
        self.value = value

    def accept(self, visitor: VisitorFwd):
        return visitor.visit_literal_expr(self)


class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: VisitorFwd):
        return visitor.visit_logical_expr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor: VisitorFwd):
        return visitor.visit_unary_expr(self)


class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: VisitorFwd):
        return visitor.visit_variable_expr(self)


class Visitor:
    def visit_assign_expr(self, expr: Assign):
        raise NotImplementedError

    def visit_binary_expr(self, expr: Binary):
        raise NotImplementedError

    def visit_grouping_expr(self, expr: Grouping):
        raise NotImplementedError

    def visit_literal_expr(self, expr: Literal):
        raise NotImplementedError

    def visit_logical_expr(self, expr: Logical):
        raise NotImplementedError

    def visit_unary_expr(self, expr: Unary):
        raise NotImplementedError

    def visit_variable_expr(self, expr: Variable):
        raise NotImplementedError
