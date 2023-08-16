from typing import Optional


class ReturnValue(Exception):
    def __init__(self, value: Optional[object]) -> None:
        self.value: Optional[object] = value
