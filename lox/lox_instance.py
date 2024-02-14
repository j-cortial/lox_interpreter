from lox.lox_class import LoxClass


class LoxInstance:
    def __init__(self, klass: LoxClass) -> None:
        self.klass = klass

    def __str__(self) -> str:
        return f"{self.klass.name} instance"
