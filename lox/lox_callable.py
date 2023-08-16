from typing import Optional, TypeAlias

InterpreterFwd: TypeAlias = "lox.interpreter.Interpreter"

class LoxCallable:
    def arity(self) -> int:
        raise NotImplementedError

    def call(self, interpreter: InterpreterFwd, arguments: list[object]) -> Optional[object]:
        raise NotImplementedError
