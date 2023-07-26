from lox.tokens import Token
from lox.runtime_error import InterpreterRuntimeError

from typing import Optional

class Environment:
    def __init__(self) -> None:
        self.values: dict[str, object] = dict()

    def get(self, name: Token) -> object:
        value: Optional[object] = self.values.get(name.lexeme)
        if value is not None:
            return value
        raise InterpreterRuntimeError(name, f"Undefined variable '{name.lexeme}'")

    def define(self, name: str, value: object) -> None:
        self.values[name] = value
