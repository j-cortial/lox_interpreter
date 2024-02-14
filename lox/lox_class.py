class LoxClass:
    def __init__(self, name: str) -> None:
        self.name: str = name

    def __str__(self) -> str:
        return self.name
