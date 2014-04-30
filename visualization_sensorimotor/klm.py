# -*- coding: utf-8 -*-


import sys
import re


def main():
    if(len(sys.argv) > 1):
        with open(sys.argv[1], 'r') as f:
            parse_file(f)
    else:
        pass


def parse_file(file):
    operators = []
    operators_map = {}
    for line in file:
        line = remove_comment(line)
        if len(line) > 0:
            operators = operators + parse_line(line)
    for sequence in operators:
        results = re.search(r'[0-9]+', sequence)
        if results is not None:
            count = (int)(results.group())
        else:
            count = 1

        results = re.search(r'[a-zA-Z]+', sequence)
        if results is not None:
            operator = results.group()

        if operator in operators_map:
            operators_map[operator] = operators_map[operator] + count
        else:
            operators_map[operator] = count
    compute_time(operators_map)


def compute_time(operators_map):
    time = {'k': 10, 'm': 10, 'k': 10, }
    for key in operators_map:
        print time[key], " * ", operators_map[key]


def remove_comment(line):
    results = re.search(r'#', line)
    if results is not None:
        line = line[0:results.start()]
    return line


def parse_line(line):
    results = re.findall(r'[0-9]*[a-zA-Z]{1}', line)
    return results


if __name__ == '__main__':
    main()
