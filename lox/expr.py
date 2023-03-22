from abc import ABC, abstractmethod
from lox.lox_token import Token


class ExprVisitor(ABC):
    @abstractmethod
    def visit_binary_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_call_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_get_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_this_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_logical_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_set_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_variable_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_assign_expr(self, expr: "Expr"):
        pass


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor) -> None:
        pass


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return "BinaryExpr " + str(self.left) + str(self.operator) + str(self.right)

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_binary_expr(self)


class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, arguments: list[Expr]) -> None:
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def __str__(self) -> str:
        return "CallExpr " + str(self.callee) + str(self.paren) + str(self.arguments)

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_call_expr(self)


class Get(Expr):
    def __init__(self, object: Expr, name: Token) -> None:
        self.object = object
        self.name = name

    def __str__(self) -> str:
        return "GetExpr " + str(self.object) + str(self.name)

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_get_expr(self)


class This(Expr):
    def __init__(self, keyword: Token) -> None:
        self.keyword = keyword

    def __str__(self) -> str:
        return "ThisExpr " + str(self.keyword)

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_this_expr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def __str__(self) -> str:
        return "GroupingExpr " + str(self.expression)

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self, value: object) -> None:
        self.value = value

    def __str__(self) -> str:
        return "LiteralExpr " + str(self.value)

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_literal_expr(self)


class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return "LogicalExpr " + str(self.left) + str(self.operator) + str(self.right)

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_logical_expr(self)


class Set(Expr):
    def __init__(self, object: Expr, name: Token, value: Expr) -> None:
        self.object = object
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return "SetExpr " + str(self.object) + str(self.name) + str(self.value)

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_set_expr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr) -> None:
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return "UnaryExpr " + str(self.operator) + str(self.right)

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_unary_expr(self)


class Variable(Expr):
    def __init__(self, name: Token) -> None:
        self.name = name

    def __str__(self) -> str:
        return "VariableExpr " + str(self.name)

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_variable_expr(self)


class Assign(Expr):
    def __init__(self, name: Token, value: Expr) -> None:
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return "AssignExpr " + str(self.name) + str(self.value)

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_assign_expr(self)
