from typing import Optional
from lox.lox_class import LoxClass
from lox.runtime_error import InterpreterRuntimeError
from lox.tokens import Token


class LoxInstance:
    def __init__(self, klass: LoxClass) -> None:
        self.klass: LoxClass = klass
        self.fields: dict[str, object] = {}

    def __str__(self) -> str:
        return f"{self.klass.name} instance"

    def get(self, name: Token) -> object:
        from lox.lox_function import LoxFunction
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method: Optional[LoxFunction] = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        raise InterpreterRuntimeError(name, f"Undefined property {name.lexeme}")

    def set(self, name: Token, value: object) -> None:
        self.fields[name.lexeme] = value
