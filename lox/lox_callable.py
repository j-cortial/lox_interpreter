from interpreter import Interpreter


class LoxCallable:
    def arity(self) -> int:
        raise NotImplementedError

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        raise NotImplementedError
