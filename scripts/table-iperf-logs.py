from collections import defaultdict
from itertools import repeat
import re
from statistics import mean, median
import sys


def load_log_file(log_file_path):
    with open(log_file_path, 'r') as f:
        for l in f:
            try:
                _, _, time, _, size, _, bandwidth, _ = l.split()
            except ValueError:
                continue

            time = float(time.split('-')[1])
            size = float(size)
            bandwidth = float(bandwidth)

            yield time, size, bandwidth


split = 16 * 1024
testname_match = re.compile(r'.*-(\d+)-([a-z]+).txt')
cw = 14


def make_row(iter):
    def tostr(x):
        match x:
            case float(): return f'{x:{cw}.4f}'
            case int(): return f'{x:{cw}d}'
            case str(): return x.rjust(cw)
            case None: return ' ' * cw
            case tuple(): return ' '.join(map(tostr, x))

    return ' '.join(map(tostr, iter)) + '\n'


if __name__ == '__main__':
    tests = defaultdict(dict)
    other = list()

    for arg in sys.argv[1:]:
        r = defaultdict(list)
        for t, s, bw in load_log_file(arg):
            r[s].append(bw)

        if match := testname_match.match(arg):
            date, k = match.groups()
            tests[int(date)][k] = r
        else:
            other.append(r)

    # allkinds = {k for kinds in tests.values() for k in kinds.keys()}
    allkinds = ['codel', 'pfifo', 'age']

    table = make_row(['date', 'flowsize', *zip(repeat(None), allkinds)])
    table += make_row([None, 'KiB'] + ['nflows', 'mean_bw_mbps'] * len(allkinds))
    for date, test in tests.items():
        allsizes = {size for result in test.values() for size in result.keys()}
        if allsizes:
            table += '\n'
        for size in sorted(allsizes):
            table += make_row(
                [date, int(size/1024)] +
                [(len(test[k][size]), mean(test[k][size])/10**6)
                    if k in test
                    else (None, None)
                    for k in allkinds])

    print(table)
