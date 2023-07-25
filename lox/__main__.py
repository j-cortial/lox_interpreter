import sys
from typing import Optional

from lox.runtime_error import InterpreterRuntimeError

from lox.interpreter import Interpreter

had_error: bool = False
had_runtime_error: bool = False
interpreter: Interpreter = Interpreter()


def main() -> None:
    if len(sys.argv) > 2:
        print("Usage: pylox [script]")
        exit(64)
    if len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()


def run_file(path: str) -> None:
    data = open(path).read().encode("ascii")
    run(data.decode("ascii"))

    # Indicate an error in the exit code.
    global had_error, had_runtime_error
    if had_error:
        exit(65)
    if had_runtime_error:
        exit(70)


def run_prompt() -> None:
    try:
        while True:
            line: str = input("> ")
            if line == " ":
                break
            run(line)
            global had_error
            had_error = False
    except EOFError:
        pass


def run(source: str) -> None:
    from lox.scanner import Scanner
    from lox.parser import Parser
    from lox.tokens import Token
    from lox.expr import Expr

    scanner = Scanner(source)
    tokens: list[Token] = scanner.scan_tokens()

    parser = Parser(tokens)
    expression: Optional[Expr] = parser.parse()

    # Stop if there was a syntax error
    if expression is None or had_error:
        return

    interpreter.interpret(expression)


def error(line: int, message: str) -> None:
    report(line, "", message)


def runtime_error(error: InterpreterRuntimeError) -> None:
    print(f"{error}\n[line {error.token.line}]", file=sys.stderr)
    global had_runtime_error
    had_runtime_error = True


def report(line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error {where}: {message}", file=sys.stderr)
    global had_error
    had_error = True


if __name__ == "__main__":
    main()
