#!/usr/bin/env python3

from sys import argv
from lox.lox import Lox


def main(args: list[str]) -> None:
    lox = Lox()
    if len(args) == 1:
        lox.run_file(args[0])
    else:
        lox.run_prompt()


main(argv[1:])
