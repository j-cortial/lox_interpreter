from tokens import Token


class Expr:
    pass


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right


class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression


class Literal(Expr):
    def __init__(self, value: object) -> None:
        self.value: object = value


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr) -> None:
        self.operator: Token = operator
        self.right: Expr = right
