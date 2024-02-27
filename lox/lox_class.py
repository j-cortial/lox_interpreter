from typing import Optional
from lox.lox_callable import LoxCallable
from lox.lox_function import LoxFunction


class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: dict[str, LoxFunction]) -> None:
        self.name: str = name
        self.methods: dict[str, LoxFunction] = methods

    def __str__(self) -> str:
        return self.name

    def find_method(self, name: str) -> Optional[LoxFunction]:
        if name in self.methods:
            return self.methods[name]

    def call(self, interpreter, arguments: list[object]) -> Optional[object]:
        from lox.lox_instance import LoxInstance

        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self) -> int:
        initializer = self.find_method("init")
        return 0 if initializer is None else initializer.arity()
