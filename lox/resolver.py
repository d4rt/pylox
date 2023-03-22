#!/usr/bin/env python3

from lox.expr import *
from lox.stmt import *
from lox.lox_token import Token

from enum import Enum


class FunctionType(Enum):
    NONE = 0
    FUNCTION = 1


class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, lox: "Lox", interpreter: "Interpreter"):
        super().__init__()
        self.lox = lox
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.NONE

    def resolve(self, obj):
        if isinstance(obj, list):
            for o in obj:
                o.accept(self)
        else:
            obj.accept(self)

    def resolve_local(self, expr: Expr, name: Token):
        for distance, scope in enumerate(self.scopes[::-1]):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, distance)
                return

    def resolve_function(self, function: Function, type: FunctionType):
        enclosing_function = self.current_function
        self.current_function = type

        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()

        self.current_function = enclosing_function

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            self.lox.parse_error(
                name, "Already a variable with this name in this scope."
            )
        scope[name.lexeme] = False

    def define(self, name: Token):
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        scope[name.lexeme] = True

    def visit_block_stmt(self, stmt: Block):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    def visit_expression_stmt(self, stmt: Expression):
        self.resolve(stmt.expression)

    def visit_function_stmt(self, stmt: Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_if_stmt(self, stmt: If):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch:
            self.resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print):
        self.resolve(stmt.expression)

    def visit_return_stmt(self, stmt: Return):
        if self.current_function == FunctionType.NONE:
            self.lox.parse_error(stmt.keyword, "Can't return from top-level code.")
        if stmt.value:
            self.resolve(stmt.value)

    def visit_var_stmt(self, stmt: Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visit_while_stmt(self, stmt: While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_variable_expr(self, expr: Variable):
        if len(self.scopes) != 0 and self.scopes[-1].get(expr.name.lexeme) == False:
            self.lox.parse_error(
                expr.name, "Can't read local variable in its own initializer."
            )
        self.resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr: Assign):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr: Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call_expr(self, expr: Call):
        self.resolve(expr.callee)
        for arg in expr.arguments:
            self.resolve(arg)

    def visit_grouping_expr(self, expr: Grouping):
        self.resolve(expr.expression)

    def visit_literal_expr(self, lit: Literal):
        pass

    def visit_logical_expr(self, expr: Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_unary_expr(self, expr: Unary):
        self.resolve(expr.right)
