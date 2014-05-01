# -*- coding: utf-8 -*-


import sys
import re


def main():
    if(len(sys.argv) > 1):
        with open(sys.argv[1], 'r') as f:
            parse_file(f)


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
            operator = results.group().lower()
        else:
            operator = None

        if operator is None:
            continue
        else:
            if operator in operators_map:
                operators_map[operator] = operators_map[operator] + count
            else:
                operators_map[operator] = count
    compute_time(operators_map)


def compute_time(operators_map):
    #k: keystroke
    #p: point with mouse to a target on a display
    #b: press or release mouse button
    #h: home hands to keyboard or mouse
    #m: mental act of rountine thinking
    #w: waiting time for the system to respond (negligible)
    standard_operator_time = {'k': 0.28, 'p': 1.1, 'b': 0.1, 'h': 0.4, 'm': 1.2}
    time = 0
    for key in operators_map:
        if key in standard_operator_time:
            print key, ": ", standard_operator_time[key], "*", operators_map[key]
            time += operators_map[key] * standard_operator_time[key]
    print "The overall time to complete the task was", time, "seconds"


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
