from token_types import TokenType
from tokens import Token

keywords: dict[str, TokenType] = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


class Scanner:
    def __init__(self, source: str) -> None:
        self.source: str = source
        self.tokens: list[Token] = []
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1

    def scan_tokens(self) -> list[Token]:
        while not self.at_end():
            # We are at the beginning of the next lexeme
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self) -> None:
        match self.advance():
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
                )
            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS
                )
            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
                )
            case "/":
                if self.match("/"):
                    # A comment goes until the end of the line
                    while self.peek() != "\n" and not self.at_end():
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1
            case '"':
                self.string()
            case c:
                if self.is_digit(c):
                    self.number()
                elif self.is_alpha(c):
                    self.identifier()
                else:
                    import lox

                    lox.error(self.line, f"Unexpected character: {c}")

    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()
        text: str = self.source[self.start : self.current]
        type: TokenType = keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(type, text)

    def number(self) -> None:
        while self.is_digit(self.peek()):
            self.advance()

        # Look for a fraction part
        if self.peek() == "." and self.is_digit(self.peek_next()):
            # Consume the '.'
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def string(self) -> None:
        while self.peek() != '"' and not self.at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.at_end():
            import lox

            lox.error(self.line, "Unterminated string")
            return

        # The closing '"'
        self.advance()

        # Trim the surrounding quotes
        value: str = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def match(self, expected: str) -> bool:
        if self.at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self) -> str:
        if self.at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def is_alpha(self, c: str) -> bool:
        return len(c) == 1 and (
            (c[0] >= "a" and c[0] <= "z")
            or (c[0] >= "A" and c[0] <= "Z")
            or c[0] == "_"
        )

    def is_digit(self, c: str) -> bool:
        return len(c) == 1 and c[0] >= "0" and c[0] <= "9"

    def is_alphanumeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)

    def advance(self) -> str:
        res = self.source[self.current]
        self.current += 1
        return res

    def add_token(self, type: TokenType, literal: object | None = None) -> None:
        text: str = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, literal, self.line))
