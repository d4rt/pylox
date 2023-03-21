#!/usr/bin/env python3

from lox.expr import *


class ASTPrinter(ExprVisitor):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def parenthesize(self, name: str, *exprs: Expr) -> str:
        return f"({name} {' '.join([e.accept(self) for e in exprs])})"

    def visit_binary_expr(self, expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)


class RPNPrinter(ExprVisitor):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary) -> str:
        left = expr.left.accept(self)
        right = expr.right.accept(self)
        return f"{left} {right} {expr.operator.lexeme}"

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return expr.expression.visit(self)

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        if expr.operator.lexeme == "!":
            return f"{expr.right.accept(self)} NOT"
        elif expr.operator.lexeme == "-":
            return f"{expr.right.accept(self)} NEGATE"
