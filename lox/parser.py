from lox.tokens import Token
from lox.token_types import TokenType
import lox.expr as expr
from lox.expr import Expr
import lox.stmt as stmt
from lox.stmt import Stmt

from typing import Optional


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens: list[Token] = tokens
        self.current: int = 0

    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.is_at_end():
            statement: Optional[Stmt]= self.declaration()
            if statement is not None:
                statements.append(statement)
        return statements

    def declaration(self) -> Optional[Stmt]:
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()

    def var_declaration(self)  -> Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect variable name")
        initializer: Optional[Expr] = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable initialization")
        return stmt.Var(name, initializer)

    def statement(self) -> Stmt:
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.LEFT_BRACE):
            return stmt.Block(self.block())
        return self.expression_statement()

    def print_statement(self) -> Stmt:
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value")
        return stmt.Print(value)

    def expression_statement(self) -> Stmt:
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression")
        return stmt.Expression(expr)

    def block(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statement: Optional[Stmt]= self.declaration()
            if statement is not None:
                statements.append(statement)
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block")
        return statements

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expression: Expr = self.equality()
        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()
            if type(expression) is expr.Variable:
                name: Token = expression.name
                return expr.Assign(name, value)
            self.error(equals, "Invalid assignment target.")
        return expression

    def equality(self) -> Expr:
        expression: Expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expression = expr.Binary(expression, operator, right)
        return expression

    def comparison(self) -> Expr:
        expression: Expr = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator: Token = self.previous()
            right: Expr = self.term()
            expression = expr.Binary(expression, operator, right)
        return expression

    def term(self) -> Expr:
        expression: Expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self.previous()
            right: Expr = self.factor()
            expression = expr.Binary(expression, operator, right)
        return expression

    def factor(self) -> Expr:
        expression: Expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: Expr = self.unary()
            expression = expr.Binary(expression, operator, right)
        return expression

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr = self.unary()
            return expr.Unary(operator, right)
        return self.primary()

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return expr.Literal(False)
        if self.match(TokenType.TRUE):
            return expr.Literal(True)
        if self.match(TokenType.NIL):
            return expr.Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return expr.Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return expr.Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expression: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
            return expr.Grouping(expression)

        raise self.error(self.peek(), "Expect expression")

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        import lox.__main__ as __main__

        __main__.error(token.line, message)
        return ParseError()

    def synchronize(self) -> None:
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            match self.peek().type:
                case TokenType.CLASS | TokenType.FUN | TokenType.VAR | TokenType.FOR | TokenType.IF | TokenType.WHILE | TokenType.PRINT | TokenType.RETURN:
                    return

            self.advance()

    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]
