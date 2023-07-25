from lox.token_types import TokenType


class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: object | None, line: int) -> None:
        self.type: TokenType = type
        self.lexeme: str = lexeme
        self.literal: object | None = literal
        self.line: int = line

    def __str__(self) -> str:
        return f"{self.type} {self.lexeme} {self.literal}"
