from abc import ABC, abstractmethod
from lox.lox_token import Token
from lox.expr import Expr


class StmtVisitor(ABC):
    @abstractmethod
    def visit_block_stmt(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_expression_stmt(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_function_stmt(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_if_stmt(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_while_stmt(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_print_stmt(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_return_stmt(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_var_stmt(self, expr: "Expr"):
        pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor) -> None:
        pass


class Block(Stmt):
    def __init__(self, statements: list[Stmt]) -> None:
        self.statements = statements

    def __str__(self) -> str:
        return "BlockStmt "  + str(self.statements)

    def accept(self, visitor: StmtVisitor) -> None:
        return visitor.visit_block_stmt(self)


class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def __str__(self) -> str:
        return "ExpressionStmt "  + str(self.expression)

    def accept(self, visitor: StmtVisitor) -> None:
        return visitor.visit_expression_stmt(self)


class Function(Stmt):
    def __init__(self, name: Token, params: list[Token], body: list[Stmt]) -> None:
        self.name = name
        self.params = params
        self.body = body

    def __str__(self) -> str:
        return "FunctionStmt "  + str(self.name) + str(self.params) + str(self.body)

    def accept(self, visitor: StmtVisitor) -> None:
        return visitor.visit_function_stmt(self)


class If(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __str__(self) -> str:
        return "IfStmt "  + str(self.condition) + str(self.then_branch) + str(self.else_branch)

    def accept(self, visitor: StmtVisitor) -> None:
        return visitor.visit_if_stmt(self)


class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt) -> None:
        self.condition = condition
        self.body = body

    def __str__(self) -> str:
        return "WhileStmt "  + str(self.condition) + str(self.body)

    def accept(self, visitor: StmtVisitor) -> None:
        return visitor.visit_while_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def __str__(self) -> str:
        return "PrintStmt "  + str(self.expression)

    def accept(self, visitor: StmtVisitor) -> None:
        return visitor.visit_print_stmt(self)


class Return(Stmt):
    def __init__(self, keyword: Token, value: Expr) -> None:
        self.keyword = keyword
        self.value = value

    def __str__(self) -> str:
        return "ReturnStmt "  + str(self.keyword) + str(self.value)

    def accept(self, visitor: StmtVisitor) -> None:
        return visitor.visit_return_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr) -> None:
        self.name = name
        self.initializer = initializer

    def __str__(self) -> str:
        return "VarStmt "  + str(self.name) + str(self.initializer)

    def accept(self, visitor: StmtVisitor) -> None:
        return visitor.visit_var_stmt(self)
