#!/usr/bin/env python3

from lox.expr import *
from lox.stmt import *
from lox.lox_token import Token, TokenType
from lox.errors import LoxRuntimeError
from lox.environment import Environment
from dataclasses import dataclass
from abc import ABC
from time import time

class LoxCallable(ABC):
    def call(self, interpreter: 'Interpreter', arguments: list):
        raise NotImplementedError
    def arity(self) -> int:
        raise NotImplementedError

class ClockCallable(LoxCallable):
    def call(self, interpreter: 'Interpreter', arguments: list):
        return float(time())
    def arity(self) -> int:
        return 0
    def __str__(self) -> str:
        return "<native fn>"

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter: 'Interpreter', arguments: list):
        env = Environment(self.closure)
        for p, a in zip(self.declaration.params, arguments):
            env.define(p.lexeme, a)
        try:
            interpreter.execute_block(self.declaration.body, env)
        except Return as r:
            return r.value

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

class Return(RuntimeError):
    def __init__(self, value):
        super().__init__()
        self.value = value

class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, lox: "Lox", env: Environment = Environment()):
        super().__init__()
        self.lox = lox
        self.global_environment = env
        self.environment = self.global_environment
        self.global_environment.define("clock", ClockCallable())

    def interpret(self, statements: list[Stmt]):
        try:
            for stmt in statements:
                self.execute(stmt)
        except LoxRuntimeError as e:
            self.lox.runtime_error(e)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)

    def visit_if_stmt(self, stmt: If) -> None:
        if Interpreter.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        val = self.evaluate(stmt.expression)
        print(self.stringify(val))

    def visit_return_stmt(self, stmt: Return):
        val = None
        if stmt.value is not None:
            val = self.evaluate(stmt.value)
        raise Return(val)

    def visit_var_stmt(self, stmt: Var) -> None:
        val = None
        if stmt.initializer is not None:
            val = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, val)

    def visit_while_stmt(self, stmt: While) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_block_stmt(self, stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(enclosing=self.environment))

    def visit_assign_expr(self, expr: Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_variable_expr(self, expr: Variable):
        return self.environment.get(expr.name)

    def visit_literal_expr(self, expr: Literal):
        return expr.value

    def visit_logical_expr(self, expr: Logical):
        left = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if Interpreter.is_truthy(left):
                return left
            return self.evaluate(expr.right)
        if expr.operator.type == TokenType.AND:
            if Interpreter.is_truthy(left):
                return self.evaluate(expr.right)
            return left

    def visit_grouping_expr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def execute(self, stmt: Stmt):
        return stmt.accept(self)

    def execute_block(self, statements: list[Stmt], env: Environment):
        previous = self.environment
        try:
            self.environment = env
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def visit_unary_expr(self, expr: Unary):
        right = self.evaluate(expr.right)
        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -right
        if expr.operator.type == TokenType.BANG:
            return not Interpreter.is_truthy(right)
        return None

    @staticmethod
    def is_truthy(obj) -> bool:
        if obj is None:
            return False
        if type(obj) == bool:
            return obj
        return True

    @staticmethod
    def is_equal(a, b) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        if type(a) != type(b):
            return False
        return a == b

    @staticmethod
    def check_number_operand(operator: Token, obj) -> None:
        if isinstance(obj, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")

    @staticmethod
    def check_number_operands(operator: Token, left, right) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operands must be numbers.")

    @staticmethod
    def stringify(obj) -> str:
        if obj is None:
            return "nil"
        if isinstance(obj, float):
            text = str(obj)
            if text[-2:] == ".0":
                return text[:-2]
            return text
        if isinstance(obj, bool):
            if obj:
                return "true"
            return "false"
        return str(obj)

    def visit_binary_expr(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        t = expr.operator.type
        if t == TokenType.MINUS:
            Interpreter.check_number_operands(expr.operator, left, right)
            return left - right
        if t == TokenType.SLASH:
            Interpreter.check_number_operands(expr.operator, left, right)
            return left / right
        if t == TokenType.STAR:
            Interpreter.check_number_operands(expr.operator, left, right)
            return left * right
        if t == TokenType.PLUS:
            if isinstance(left, (str, float)) and isinstance(right, (str, float)):
                if type(left) == type(right):
                    return left + right
            raise LoxRuntimeError(
                expr.operator, "Operands must be two numbers or two strings."
            )
        if t == TokenType.GREATER:
            Interpreter.check_number_operands(expr.operator, left, right)
            return left > right
        if t == TokenType.GREATER_EQUAL:
            Interpreter.check_number_operands(expr.operator, left, right)
            return left >= right
        if t == TokenType.LESS:
            Interpreter.check_number_operands(expr.operator, left, right)
            return left < right
        if t == TokenType.LESS_EQUAL:
            Interpreter.check_number_operands(expr.operator, left, right)
            return left <= right
        if t == TokenType.BANG_EQUAL:
            return not Interpreter.is_equal(left, right)
        if t == TokenType.EQUAL_EQUAL:
            return Interpreter.is_equal(left, right)
        return None

    def visit_call_expr(self, expr: Call):
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
        if len(arguments) != callee.arity():
            raise LoxRuntimeError(expr.paren,f"Expected {callee.arity()} arguments but got {len(arguments)}.")
        return callee.call(self, arguments)

    def visit_function_stmt(self, stmt: Function):
        fn = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, fn)
