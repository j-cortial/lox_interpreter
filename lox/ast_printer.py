import expr
from expr import Expr
from tokens import Token
from token_types import TokenType


class AstPrinter(expr.Visitor):
    def print(self, expr: Expr) -> None:
        return expr.accept(self)

    def visit_binary_expr(self, expr: expr.Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: expr.Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: expr.Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: expr.Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name: str, *args: Expr) -> str:
        builder: list[str] = []
        builder.append(f"({name}")
        for expr in args:
            text: str = expr.accept(self)
            builder.append(f" {text}")
        builder.append(")")
        return "".join(builder)


def main():
    expression: Expr = expr.Binary(
        expr.Unary(Token(TokenType.MINUS, "-", None, 1), expr.Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        expr.Grouping(expr.Literal(45.67)),
    )
    print(AstPrinter().print(expression))


if __name__ == "__main__":
    main()
