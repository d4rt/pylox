#!/usr/bin/env python3


from dataclasses import dataclass, field

from lox.lox_token import TokenType, Token
from lox.expr import *
from lox.stmt import *


class ParseError(RuntimeError):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token


@dataclass
class Parser:
    tokens: list[Token] = field(default_factory=list)
    current: int = 0
    lox: "Lox" = None

    def parse(self) -> list[Stmt]:
        statements = []
        while not self.isAtEnd():
            statements.append(self.declaration())
        return statements

    def declaration(self) -> Stmt:
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FUN):
                return self.function_declaration("function")
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def class_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            methods.append(self.function_declaration("method"))
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return Class(name, methods)

    def function_declaration(self, kind: str) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(
                self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
            )
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(
                    self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        self.consume(TokenType.LEFT_BRACE, "Expect '{' before " + kind + " body.")
        body = self.block()
        return Function(name, parameters, body)

    def var_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expr = self.log_or()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                return Assign(expr.name, value)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)
            self.error(equals, "Invalid assignment target.")
        return expr

    def statement(self) -> Stmt:
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        return self.expression_statement()

    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")

        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)

    def block(self) -> list[Stmt]:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ; after value")
        return Print(value)

    def return_statement(self) -> Stmt:
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def while_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        cond = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return While(cond, body)

    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        if self.match(TokenType.SEMICOLON):
            cond = Literal(True)
        else:
            cond = self.expression()
            self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition")

        if self.match(TokenType.RIGHT_PAREN):
            inc = None
        else:
            inc = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()
        if inc is not None:
            body = Block([body, inc])

        body = While(cond, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def log_or(self) -> Expr:
        expr = self.log_and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.log_and()
            expr = Logical(expr, operator, right)

        return expr

    def log_and(self) -> Expr:
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)

        return expr

    def equality(self) -> Expr:
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.call()

    def call(self) -> Expr:
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(
                    TokenType.IDENTIFIER, "Expect property name after '.'."
                )
                expr = Get(expr, name)
            else:
                break

        return expr

    def finish_call(self, callee: Expr) -> Expr:
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        if self.match(TokenType.THIS):
            return This(self.previous())
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect expression.")

    def match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        self.lox.parse_error(token, message)
        return ParseError(token, message)

    def synchronize(self) -> None:
        self.advance()
        while not self.isAtEnd():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in {
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            }:
                return
            self.advance()

    def check(self, token_type: TokenType) -> bool:
        if self.isAtEnd():
            return False
        return self.peek().type == token_type

    def peek(self) -> Token:
        return self.tokens[self.current]

    def advance(self) -> Token:
        if not self.isAtEnd():
            self.current += 1
        return self.previous()

    def isAtEnd(self) -> bool:
        return self.current >= len(self.tokens) - 1

    def previous(self) -> Token:
        return self.tokens[self.current - 1]
