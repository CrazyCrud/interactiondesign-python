# -*- coding: utf-8 -*-


import sys
import re


def main():
    if(len(sys.argv) > 1):
        with f as open(sys.argv[1], 'r'):
            parse_file(f)
    else:
        pass


def parse_file(file):
    operators = []
    for line in file:
        operators.append(parse_line(line))


def parse_line(line):
    pass


if __name__ = '__main__':
    main()
