#!/usr/bin/env python3

from sys import argv, exit
from pathlib import Path


class GenerateAST:
    EXPR_IMPORTS = """from abc import ABC, abstractmethod
from lox.lox_token import Token


"""
    STMT_IMPORTS = """from abc import ABC, abstractmethod
from lox.lox_token import Token
from lox.expr import Expr


"""

    EXPRS = {
        "Binary": ["left: Expr", "operator: Token", "right: Expr"],
        "Grouping": ["expression: Expr"],
        "Literal": ["value: object"],
        "Logical": ["left: Expr", "operator: Token", "right: Expr"],
        "Unary": ["operator: Token", "right: Expr"],
        "Variable": ["name: Token"],
        "Assign": ["name: Token", "value: Expr"],
    }
    STMT = {
        "Block": ["statements: list[Stmt]"],
        "Expression": ["expression: Expr"],
        "If": ["condition: Expr", "then_branch: Stmt", "else_branch: Stmt"],
        "While": ["condition: Expr", "body: Stmt"],
        "Print": ["expression: Expr"],
        "Var": ["name: Token", "initializer: Expr"],
    }

    @staticmethod
    def main(args: list[str]):
        if len(args) != 1:
            print("Usage generate_ast <output_directory>")
            exit(64)
        output_path = Path(args[0]).resolve()
        GenerateAST.define_ast(
            output_path / "expr.py", "Expr", GenerateAST.EXPRS, GenerateAST.EXPR_IMPORTS
        )
        GenerateAST.define_ast(
            output_path / "stmt.py", "Stmt", GenerateAST.STMT, GenerateAST.STMT_IMPORTS
        )

    @staticmethod
    def define_ast(output_file: Path, base: str, types: dict, imports: str) -> None:
        with output_file.open(mode="w", encoding="utf-8") as f:
            f.write(imports)
            f.write(f"""class {base}Visitor(ABC):\n""")
            for t in types:
                f.write(
                    f"""    @abstractmethod
    def visit_{t.lower()}_{base.lower()}(self, expr: "Expr"):
        pass

"""
                )
            f.write(
                f"""
class {base}(ABC):
    @abstractmethod
    def accept(self, visitor: {base}Visitor) -> None:
        pass
"""
            )
            for t in types:
                f.write("\n\n")
                f.write(
                    f"""class {t}({base}):
    def __init__(self, {", ".join(types[t])}) -> None:
"""
                )
                for field in types[t]:
                    field_name = field.split(":")[0]
                    f.write(f"        self.{field_name} = {field_name}\n")
                f.write(
                    f"""
    def __str__(self) -> str:
        return "{t}{base} "  + """
                )
                f.write(
                    " + ".join(
                        [
                            ("str(self." + field.split(":")[0] + ")")
                            for field in types[t]
                        ]
                    )
                )
                f.write(
                    f"""

    def accept(self, visitor: {base}Visitor) -> None:
        return visitor.visit_{t.lower()}_{base.lower()}(self)
"""
                )


if __name__ == "__main__":
    GenerateAST.main(argv[1:])
