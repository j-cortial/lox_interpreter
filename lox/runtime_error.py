from lox.tokens import Token


class InterpreterRuntimeError(Exception):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token: Token = token
