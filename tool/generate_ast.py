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
            "Assign   => name: Token, value: Expr",
            "Binary   => left: Expr, operator: Token, right: Expr",
            "Call     => callee: Expr, paren: Token, arguments: list[Expr]",
            "Grouping => expression: Expr",
            "Literal  => value: object",
            "Logical  => left: Expr, operator: Token, right: Expr",
            "Unary    => operator: Token, right: Expr",
            "Variable => name: Token",
        ],
        imports=[("tokens", "Token")],
    )
    define_ast(
        output_dir,
        "Stmt",
        [
            "Block      => statements: list[Stmt]",
            "Expression => expression: Expr",
            "Function   => name: Token, params: list[Token], body: list[Stmt]",
            "If         => condition: Expr, then_branch: Stmt, else_branch: Stmt | None",
            "Print      => expression: Expr",
            "Return     => keyword: Token, value: Expr | None",
            "Var        => name: Token, initializer: Expr | None",
            "While      => condition: Expr, body: Stmt",
        ],
        imports=[("expr", "Expr"), ("tokens", "Token")],
    )


indent: str = " " * 4


def define_ast(
    output_dir: str, base_name: str, types: list[str], imports: list[tuple[str, str]]
) -> None:
    path: str = f"{output_dir}/{base_name.lower()}.py"

    with open(path, "w") as writer:
        for module, type in imports:
            writer.write(f"from lox.{module} import {type}\n")
        writer.write("from typing import TypeAlias\n")
        writer.write('VisitorFwd: TypeAlias = "Visitor"\n')
        writer.write(f"class {base_name}:\n")
        # The base accept() method
        writer.write(f"{indent}def accept(self, visitor: VisitorFwd):\n")
        writer.write(f"{indent * 2}raise NotImplementedError\n")
        # The AST classes
        for type in types:
            data: list[str] = type.split("=>")
            class_name: str = data[0].strip()
            fields: str = data[1].strip()
            define_type(writer, base_name, class_name, fields)
        define_visitor(writer, base_name, types)


def define_visitor(writer: io.TextIOBase, base_name: str, types: list[str]):
    writer.write(f"class Visitor:\n")
    for type in types:
        type_name: str = type.split("=>")[0].strip()
        writer.write(
            f"{indent}def visit_{type_name.lower()}_{base_name.lower()}(self, {base_name.lower()}: {type_name}):\n"
        )
        writer.write(f"{indent * 2}raise NotImplementedError\n")


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
    # Visitor pattern
    writer.write(f"{indent}def accept(self, visitor: VisitorFwd):\n")
    writer.write(
        f"{indent * 2}return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)\n"
    )


if __name__ == "__main__":
    main()
