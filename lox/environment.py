from lox.tokens import Token
from lox.runtime_error import InterpreterRuntimeError

from typing import Optional, Self


class Environment:
    def __init__(self, enclosing: Optional[Self] = None) -> None:
        self.values: dict[str, object] = dict()
        self.enclosing: Optional[Self] = enclosing

    def get(self, name: Token) -> object:
        value: Optional[object] = self.values.get(name.lexeme)
        if value is not None:
            return value
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise InterpreterRuntimeError(name, f"Undefined variable '{name.lexeme}'")

    def define(self, name: str, value: object) -> None:
        self.values[name] = value
