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
            statement: Optional[Stmt] = self.declaration()
            if statement is not None:
                statements.append(statement)
        return statements

    def declaration(self) -> Optional[Stmt]:
        try:
            if self.match(TokenType.FUN):
                return self.function("function")
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()

    def var_declaration(self) -> Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect variable name")
        initializer: Optional[Expr] = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable initialization")
        return stmt.Var(name, initializer)

    def statement(self) -> Stmt:
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return stmt.Block(self.block())
        return self.expression_statement()

    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'")

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition: Optional[Expr] = (
            self.expression() if not self.check(TokenType.SEMICOLON) else None
        )
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition")

        increment: Optional[Expr] = (
            self.expression() if not self.check(TokenType.SEMICOLON) else None
        )
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses")

        body: Stmt = self.statement()

        if increment is not None:
            body = stmt.Block([body, stmt.Expression(increment)])

        if condition is None:
            condition = expr.Literal(True)
        body = stmt.While(condition, body)

        if initializer is not None:
            body = stmt.Block([initializer, body])

        return body

    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition")

        then_branch: Stmt = self.statement()
        else_branch: Optional[Stmt] = (
            self.statement() if self.match(TokenType.ELSE) else None
        )
        return stmt.If(condition, then_branch, else_branch)

    def print_statement(self) -> Stmt:
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value")
        return stmt.Print(value)

    def while_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition")
        body: Stmt = self.statement()
        return stmt.While(condition, body)

    def expression_statement(self) -> Stmt:
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression")
        return stmt.Expression(expr)

    def function(self, kind: str) -> stmt.Function:
        name: Token = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name")
        parameters: list[Token] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Cannot have more than 255 parameters")
                parameters.append(
                    self.consume(TokenType.IDENTIFIER, "Expect parameter name")
                )
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters")
        self.consume(TokenType.LEFT_BRACE, f"Expect '\u007b' before {kind} body")
        body: list[Stmt] = self.block()
        return stmt.Function(name, parameters, body)

    def block(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statement: Optional[Stmt] = self.declaration()
            if statement is not None:
                statements.append(statement)
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block")
        return statements

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expression: Expr = self.or_expr()
        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()
            if type(expression) is expr.Variable:
                name: Token = expression.name
                return expr.Assign(name, value)
            self.error(equals, "Invalid assignment target.")
        return expression

    def or_expr(self) -> Expr:
        expression: Expr = self.and_expr()
        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self.and_expr()
            expression = expr.Logical(expression, operator, right)
        return expression

    def and_expr(self) -> Expr:
        expression: Expr = self.equality()
        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: Expr = self.equality()
            expression = expr.Logical(expression, operator, right)
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
        return self.call()

    def call(self) -> Expr:
        expression: Expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expression = self.finish_call(expression)
            else:
                break
        return expression

    def finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Cannot have more than 255 arguments")
                arguments.append(self.expression())
        paren: Token = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments")
        return expr.Call(callee, paren, arguments)

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
