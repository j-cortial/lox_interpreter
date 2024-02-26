from lox.lox_callable import LoxCallable
from lox.environment import Environment
import lox.stmt as stmt
from lox.return_value import ReturnValue

from typing import Optional


class LoxFunction(LoxCallable):
    def __init__(self, declaration: stmt.Function, closure: Environment) -> None:
        self.closure: Environment = closure
        self.declaration: stmt.Function = declaration

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

    def arity(self) -> int:
        return len(self.declaration.params)

    def bind(self, instance) -> "LoxFunction":
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment)

    def call(self, interpreter, arguments: list[object]) -> Optional[object]:
        environment: Environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnValue as e:
            return e.value
