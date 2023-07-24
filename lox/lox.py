import sys

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

    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    # For now, just print the tokens
    for t in tokens:
        print(t)


def error(line: int, message: str) -> None:
    report(line, "", message)


def report(line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error {where}: {message}", file=sys.stderr)
    global had_error
    had_error = True


if __name__ == "__main__":
    main()
