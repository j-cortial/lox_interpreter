from typing import Optional

class LoxCallable:
    def arity(self) -> int:
        raise NotImplementedError

    def call(self, interpreter, arguments: list[object]) -> Optional[object]:
        raise NotImplementedError
