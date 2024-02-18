from lox.lox_class import LoxClass
from lox.runtime_error import InterpreterRuntimeError
from lox.tokens import Token


class LoxInstance:
    def __init__(self, klass: LoxClass) -> None:
        self.klass = klass
        self.fields: dict[str, object] = dict()

    def __str__(self) -> str:
        return f"{self.klass.name} instance"

    def get(self, name: Token) -> object:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        raise InterpreterRuntimeError(name, f"Undefined property {name.lexeme}")

    def set(self, name: Token, value: object) -> None:
        self.fields[name.lexeme] = value
