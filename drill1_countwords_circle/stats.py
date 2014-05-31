import math
import sys


def calc_mean(values):
    """
        >>> calcmean([2,3,4])
        3.0
        >>> calcmean([2,10,9])
        7.0
    """
    return float(sum(values, 0.0) / len(values))


def calc_median(values):
    """
        >>> calcmedian ([2,6,9,10])
	7.5
        >>> calcmedian([2,15,3])
        3
        >>> calcmedian([3.5,7.9,10.2])
        7.9
    """
    values.sort()
    count = len(values)
    if not count % 2:
        return (values[(count/2)-1]+values[count/2])/2.0
    else:
        return values[count/2]


def calc_standarddeviation(values):
    mean = calc_mean(values)
    diffsquaresum = 0.0
    for value in values:
        diff = value-mean
        diffsquaresum += diff * diff
    standarddeviation = math.sqrt(diffsquaresum/(len(values)-1.0))
    return standarddeviation

numbers = []

if len(sys.argv) > 1:
    strnumbers = sys.argv[1:]
else:
    strnumbers = sys.stdin.read().split()

numbers = list(map(float, strnumbers))

print "input numbers: "
print numbers
print "mean: %f" % calc_mean(numbers)
print "median: %f" % calc_median(numbers)
print "standarddeviation: %f" % calc_standarddeviation(numbers)
