from lox.tokens import Token


class Expr:
    def accept(self, visitor):
        raise NotImplementedError


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self, value: object) -> None:
        self.value: object = value

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr) -> None:
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)


class Visitor:
    def visit_binary_expr(self, expr: Binary):
        raise NotImplementedError

    def visit_grouping_expr(self, expr: Grouping):
        raise NotImplementedError

    def visit_literal_expr(self, expr: Literal):
        raise NotImplementedError

    def visit_unary_expr(self, expr: Unary):
        raise NotImplementedError
