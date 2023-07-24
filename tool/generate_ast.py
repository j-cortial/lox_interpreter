import sys
import io


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: generate_ast <output directory>")
        exit(64)
    output_dir: str = sys.argv[1]
    define_ast(
        output_dir,
        "Expr",
        [
            "Binary   => left: Expr, operator: Token, right: Expr",
            "Grouping => expression: Expr",
            "Literal  => value: object",
            "Unary    => operator: Token, right: Expr",
        ],
    )


indent: str = " " * 4


def define_ast(output_dir: str, base_name: str, types: list[str]) -> None:
    path: str = f"{output_dir}/{base_name.lower()}.py"

    with open(path, "w") as writer:
        writer.write(f"from tokens import Token\n")
        writer.write(f"class {base_name}:\n")
        writer.write(f"{indent}pass\n")
        for type in types:
            data: list[str] = type.split("=>")
            class_name: str = data[0].strip()
            fields: str = data[1].strip()
            define_type(writer, base_name, class_name, fields)


def define_type(
    writer: io.TextIOBase, base_name: str, class_name: str, field_list: str
):
    writer.write(f"class {class_name}({base_name}):\n")
    # Constructor
    writer.write(f"{indent}def __init__(self, {field_list}):\n")
    # Store parameters in fields
    for field in field_list.split(","):
        name: str = field.split(":")[0].strip()
        writer.write(f"{indent * 2}self.{name} = {name}\n")


if __name__ == "__main__":
    main()
