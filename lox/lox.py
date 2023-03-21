#!/usr/bin/env python3
#
from dataclasses import dataclass
from sys import exit, stderr
from lox.scanner import Scanner
from lox.parser import Parser
from lox.lox_token import Token, TokenType
from lox.interpreter import Interpreter, LoxRuntimeError


@dataclass
class Lox:
    had_error: bool = False
    had_runtime_error: bool = False

    def run_file(self, path: str) -> None:
        with open(path, "r") as f:
            program = f.read()
            self.run(program)
        if self.had_error:
            exit(65)
        if self.had_runtime_error:
            exit(70)

    def run_prompt(self) -> None:
        while True:
            line = input("> ")
            if line == "":
                break
            self.run(line)
            self.had_error = False

    def run(self, program: str) -> None:
        scanner = Scanner(program, lox=self)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens,lox=self)
        statements = parser.parse()
        interpreter = Interpreter(lox=self)
        if self.had_error:
            return
        interpreter.interpret(statements)

    def error(self, line: int, message: str) -> None:
        self.report(line, "", message)

    def runtime_error(self, error: LoxRuntimeError) -> None:
        print(
            f"""{error}
[line {error.token.line}]
""", file=stderr
        )
        self.had_runtime_error = True

    def parse_error(self, token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)

    def report(self, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}", file=stderr)
        self.had_error = True
