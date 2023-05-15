#!/usr/bin/env python3
from dataclasses import dataclass, field
from lox.lox_token import Token, TokenType


@dataclass
class Scanner:
    source: str = ""
    tokens: list[Token] = field(default_factory=list)
    start: int = 0
    current: int = 0
    line: int = 1
    lox: "Lox" = None

    def isAtEnd(self) -> bool:
        """Have we processed all input?"""
        return self.current >= len(self.source)

    def advance(self) -> str:
        """Move parsing to the next character"""
        self.current += 1
        return self.source[self.current - 1]

    def match(self, expected: str) -> bool:
        """Conditionally advance to the next character"""
        if self.isAtEnd():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self) -> bool:
        """Look at, but do not consume the next character"""
        if self.isAtEnd():
            return "\0"
        return self.source[self.current]

    def peek_next(self) -> bool:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    @staticmethod
    def is_digit(c: str) -> bool:
        return "0" <= c <= "9"

    @staticmethod
    def is_alpha(c: str) -> bool:
        return "a" <= c <= "z" or "A" <= c <= "Z" or c == "_"

    @staticmethod
    def is_alphanumeric(c: str) -> bool:
        return Scanner.is_alpha(c) or Scanner.is_digit(c)

    def add_token(self, type: TokenType, literal: object = None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def scan_token(self):
        c = self.advance()
        if c == "(":
            self.add_token(TokenType.LEFT_PAREN)
            return
        if c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
            return
        if c == "{":
            self.add_token(TokenType.LEFT_BRACE)
            return
        if c == "}":
            self.add_token(TokenType.RIGHT_BRACE)
            return
        if c == ",":
            self.add_token(TokenType.COMMA)
            return
        if c == ".":
            self.add_token(TokenType.DOT)
            return
        if c == "-":
            self.add_token(TokenType.MINUS)
            return
        if c == "+":
            self.add_token(TokenType.PLUS)
            return
        if c == ";":
            self.add_token(TokenType.SEMICOLON)
            return
        if c == "*":
            self.add_token(TokenType.STAR)
            return
        if c == "!":
            self.add_token(TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG)
            return
        if c == "=":
            self.add_token(
                TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
            )
            return
        if c == "<":
            self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
            return
        if c == ">":
            self.add_token(
                TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
            )
            return
        if c == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.isAtEnd():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
            return
        if c in {" ", "\r", "\t"}:
            return
        if c == "\n":
            self.line += 1
            return
        if c == '"':
            self.string()
            return
        if self.is_digit(c):
            self.number()
            return
        if self.is_alpha(c):
            self.identifier()
            return

        self.lox.error(self.line, f"Unexpected character.")
        return

    def string(self):
        while self.peek() != '"' and not self.isAtEnd():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.isAtEnd():
            self.lox.error(self.line, "Unterminated string.")
            return

        self.advance()
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()
        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()
        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()
        text = self.source[self.start : self.current]
        type = Scanner.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(type)

    def scan_tokens(self) -> list[Token]:
        while not self.isAtEnd():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
