import sys
from typing import Optional

had_error: bool = False


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
    global had_error
    if had_error:
        exit(65)


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
    from scanner import Scanner
    from parser import Parser
    from tokens import Token
    from expr import Expr
    from ast_printer import AstPrinter

    scanner = Scanner(source)
    tokens: list[Token] = scanner.scan_tokens()

    parser = Parser(tokens)
    expression: Optional[Expr] = parser.parse()

    # Stop if there was a syntax error
    if expression is None or had_error:
        return

    print(AstPrinter().print(expression))


def error(line: int, message: str) -> None:
    report(line, "", message)


def report(line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error {where}: {message}", file=sys.stderr)
    global had_error
    had_error = True


if __name__ == "__main__":
    main()
