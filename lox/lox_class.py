from typing import Optional
from lox.lox_callable import InterpreterFwd, LoxCallable


class LoxClass(LoxCallable):
    def __init__(self, name: str) -> None:
        self.name: str = name

    def __str__(self) -> str:
        return self.name

    def call(
        self, interpreter: InterpreterFwd, arguments: list[object]
    ) -> Optional[object]:
        from lox.lox_instance import LoxInstance

        instance = LoxInstance(self)
        return instance

    def arity(self) -> int:
        return 0
