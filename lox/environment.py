#!/usr/bin/env python3
#
from lox.lox_token import Token
from lox.errors import LoxRuntimeError
from dataclasses import dataclass, field


@dataclass
class Environment:
    enclosing: "Environment" = None
    values: dict[str, object] = field(default_factory=dict)

    def define(self, name: str, val: object) -> None:
        self.values[name] = val

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing:
            return self.enclosing.get(name)
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values[name]

    def assign_at(self, distance: int, name: Token, val):
        self.ancestor(distance).values[name.lexeme] = val

    def ancestor(self, distance: int):
        env = self
        for _ in range(distance):
            env = env.enclosing
        return env

    def assign(self, name: Token, val: object) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = val
            return
        if self.enclosing:
            self.enclosing.assign(name, val)
            return
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
