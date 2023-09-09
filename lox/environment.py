from lox.tokens import Token
from lox.runtime_error import InterpreterRuntimeError

from typing import Optional, Self


class Environment:
    def __init__(self, enclosing: Optional[Self] = None) -> None:
        self.values: dict[str, object] = dict()
        self.enclosing: Optional[Self] = enclosing

    def ancestor(self, distance: int) -> Optional[Self]:
        environment: Optional[Self] = self
        for _ in range(distance):
            assert environment is not None
            environment = environment.enclosing
        return environment

    def get(self, name: Token) -> object:
        value: Optional[object] = self.values.get(name.lexeme)
        if value is not None:
            return value
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise InterpreterRuntimeError(name, f"Undefined variable '{name.lexeme}'")

    def get_at(self, distance: int, name: str) -> Optional[object]:
        ancestor = self.ancestor(distance)
        assert ancestor is not None
        return ancestor.values.get(name)

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            return self.enclosing.assign(name, value)
        raise InterpreterRuntimeError(name, f"Undefined variable '{name.lexeme}'")

    def assign_at(self, distance: int, name: Token, value: object) -> None:
        ancestor = self.ancestor(distance)
        assert ancestor is not None
        ancestor.values[name.lexeme] = value

    def define(self, name: str, value: Optional[object]) -> None:
        self.values[name] = value
